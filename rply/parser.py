class LRParser(object):
    def __init__(self, lr_table):
        self.lr_table = lr_table

    def parse(self, tokenizer):
        from rply.token import Token, ProductionSymbol

        lookahead = None
        lookaheadstack = []
        error_count = 0

        statestack = [0]
        symstack = [Token("$end", None)]

        state = 0
        while True:
            if lookahead is None:
                if lookaheadstack:
                    lookahead = lookaheadstack.pop()
                else:
                    lookahead = tokenizer.next()

                if lookahead is None:
                    lookahead = Token("$end", None)

            ltype = lookahead.gettokentype()
            if ltype in self.lr_table.lr_action[state]:
                t = self.lr_table.lr_action[state][ltype]
                if t > 0:
                    statestack.append(t)
                    state = t
                    symstack.append(lookahead)
                    lookahead = None
                    if error_count:
                        error_count -= 1
                    continue
                elif t < 0:
                    # reduce a symbol on the stack and emit a production
                    p = self.lr_table.grammar.productions[-t]
                    pname = p.name
                    plen = p.getlength()
                    sym = ProductionSymbol(pname, None)
                    if plen:
                        targ = symstack[-plen - 1:]
                        del targ[0]
                        del symstack[-plen:]
                        del statestack[-plen:]
                        sym.value = p.func(targ)
                        symstack.append(sym)
                        state = self.lr_table.lr_goto[statestack[-1]][pname]
                        statestack.append(state)
                    else:
                        raise NotImplementedError
                    continue
                else:
                    n = symstack[-1]
                    return n.value
            else:
                raise NotImplementedError