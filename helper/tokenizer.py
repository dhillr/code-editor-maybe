import keyword
class Tokenizer:
    def __init__(self, keywords, code: str):
        self.keywords = keywords
        self.code = code

        self.variables = []
        self.functions = []

    def convert(self, code: str):
        return code.replace("(", " ( ").replace(")", " ) ").replace(":", " : ").replace(",", " , ").replace(".", " . ")
    
    def get_strs(self, code: str):
        total = code.split("\"")
        return [elem for i, elem in enumerate(total) if i & 1]

    def tokenize(self, code: str):
        # for now
        strs = self.get_strs(code)
        if len(code) < 1: return []
        tokens = self.convert(code).replace("    ", "\t").replace("\n", " ")

        for i in strs:
            tokens = tokens.replace(i, "\x01")
        
        tokens = tokens.split(" ")
        tokens = [token for token in tokens if token]
        
        str_i = 0
        for i, token in enumerate(tokens):
            if token == "\"\x01\"":
                tokens[i] = f"\"{strs[str_i]}\""
                str_i += 1

        return tokens
    
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
                if next_token == "(":
                    colormap += "b"*len(token)
                else:
                    if "\"" in token:
                        colormap += "c"*len(token)
                    else:
                        try:
                            int(token)
                            colormap += "d"*len(token)
                        except:
                            if "import" in prev_token:
                                colormap += "e"*len(token)
                            else:
                                colormap += " "*len(token)
            if token != tokens[len(tokens)-1] and token != "" and token != "(" and next_token != "(" or code[len(code)-1] == " ": colormap += " "
        return colormap

class PythonTokenizer(Tokenizer):
    def __init__(self, code):
        super().__init__(keyword.kwlist, code)