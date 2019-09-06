import sublime
import sublime_plugin


class BracketsOperater(sublime_plugin.TextCommand):
    opening, closing = '([{', ')]}'
    parents_string = "()[]{}"
    parents = {}
    for i in range(len(opening)):
        parents[opening[i]] = closing[i]
        parents[closing[i]] = opening[i]

    threshold = 1000000

    def cover(self, left, right):
        return sublime.Region(left.a, right.b)

    def select_cursor_parents(self):
        pairs = []
        for region in self.view.sel():
            parents = self.search_parents(region.a)
            if parents:
                if pairs and parents == pairs[-1]:
                    continue
                else:
                    pairs.append(parents)
        return pairs

    # TODO: Reduce delay
    # A better scheme for searching parentheses,
    # maybe increase the search region gradually
    def search_parents(self, point):
        def search(tokens, directed_parents):
            for region, scope in tokens:
                token = contents[region.a - begin:region.b - begin]
                # skip ignore
                if (token not in self.parents_string or
                    "comment" in scope or "string" in scope or
                    "char" in scope or "symbol" in scope):
                    continue

                if token in directed_parents:
                    if stack:
                        if self.parents[stack[-1]] == token:
                            if match[1] is False:
                                stack.pop()
                            else:
                                match[0] = region
                                return True
                        else:
                            return False
                    else:
                        match[1] = region
                        stack.append(token)
                        return True
                else:
                    stack.append(token)

            return False

        def get_toks(a, b):
            return self.view.extract_tokens_with_scopes(sublime.Region(a, b))

        begin = max(point - self.threshold//2, 0)
        end = min(begin + self.threshold, self.view.size())
        ltoks, rtoks = get_toks(begin, point), get_toks(point, end)
        if not (ltoks and rtoks):
            return False
        if ltoks[-1] == rtoks[0]:
            ltoks.pop()

        stack, match = [], [False, False]
        begin, end = (ltoks if ltoks else rtoks)[0][0].a, rtoks[-1][0].b
        contents = self.view.substr(sublime.Region(begin, end))

        search(rtoks, self.closing) and search(reversed(ltoks), self.opening)

        return match[0] and match


class BracketsSelectorCommand(BracketsOperater):
    def run(self, edit):
        for p in self.select_cursor_parents():
            cover = self.cover(p[0], p[1])
            self.view.sel().add(cover)


class BracketsTransformCommand(BracketsOperater):
    def run(self, edit, to):
        for p in self.select_cursor_parents():
            if self.view.substr(p[0]) == to:
                continue
            self.view.replace(edit, p[0], to)
            self.view.replace(edit, p[1], self.parents[to])


class BracketsTakeOffCommand(BracketsOperater):
    def run(self, edit):
        parents = [p for p in self.select_cursor_parents()]
        regions = [r for p in parents for r in p]
        selections = []

        regions.sort()
        for p in parents:
            begin = p[0].a - regions.index(p[0])
            end = p[1].a - regions.index(p[1])
            selection = sublime.Region(begin, end)
            selections.append(selection)

        regions.reverse()
        for r in regions:
            self.view.erase(edit, r)

        self.view.sel().add_all(selections)
