import keyword
class Tokenizer:
    def __init__(self, keywords, code: str):
        self.keywords = keywords
        self.code = code

        self.variables = []
        self.modules = []

    def convert(self, code: str):
        return code.replace("(", " ( ").replace(")", " ) ").replace(":", " : ").replace(",", " , ").replace(".", " . ")
    
    def get_strs(self, code: str):
        total = code.split("\"")
        return ["\"" + elem + "\"" for i, elem in enumerate(total) if i & 1]

    def tokenize(self, code: str):
        # for now
        strs = self.get_strs(code)
        if len(code) < 1: return []
        tokens = self.convert(code).replace("\n", "")

        for i in strs:
            tokens = tokens.replace(i, "\n")
        
        tokens = tokens.split(" ")
        if tokens[-1] == "": tokens.pop()
        # tokens = [token for token in tokens if token]

        # merging spaces
        while "" in tokens:
            space_index = tokens.index("")
            i = space_index

            space = ""

            while tokens[i] == "":
                tokens.pop(i)
                space += " "
                if i <= 0: break
                i -= 1
                
            tokens[i] = tokens[i] + space
        
        str_i = 0
        for i, token in enumerate(tokens):
            if "\n" in token:
                tokens[i] = tokens[i].replace("\n", f"{strs[str_i]}")
                str_i += 1
        # print(tokens)

        return tokens
    
    def clear_scan(self):
        self.variables = []
        self.modules = []
    
    def scan(self, code: str):
        tokens = self.tokenize(code)
        for i, token in enumerate(tokens):
            token = token.replace("\t", "    ")
            next_token = tokens[i+1].replace("\t", "    ") if i < len(tokens)-1 else ""
            prev_token = tokens[i-1].replace("\t", "    ") if i > 0 else ""

            if next_token.strip() == "=": self.variables.append(token)
            if prev_token.strip() == "import": self.modules.append(token)

    
    def get_colormap(self, code):
        # if not code: code = self.code
        tokens = self.tokenize(code)
        colormap = ""
        for i, token in enumerate(tokens):
            token = token.replace("\t", "    ")
            next_token = tokens[i+1].replace("\t", "    ") if i < len(tokens)-1 else ""
            prev_token = tokens[i-1].replace("\t", "    ") if i > 0 else ""
            if token.strip() in self.keywords:
                colormap += "a"*len(token)
            else:
                if next_token.strip() == "(":
                    colormap += "b"*len(token)
                else:
                    if "\"" in token:
                        colormap += "c"*len(token)
                    else:
                        try:
                            int(token)
                            colormap += "d"*len(token)
                        except:
                            if token.strip() in self.modules:
                                colormap += "e"*len(token)
                            elif token.strip() in self.variables:
                                colormap += "f"*len(token)
                            else:
                                colormap += " "*len(token)
            if i != len(tokens)-1 and token != "" and token != "(" and next_token != "(" \
            and "," not in next_token and "." not in next_token and "." not in token \
            or code[len(code)-1] == " " and " " not in token: colormap += " "
        # print(len(colormap), len(code.replace("\t", "    ")))
        if len(colormap) < len(code): return " "*len(code)
        return colormap

class PythonTokenizer(Tokenizer):
    def __init__(self, code):
        super().__init__(keyword.kwlist, code)