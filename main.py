import sublime
import sublime_plugin


class BracketsOperater(sublime_plugin.TextCommand):
    left_brackets  = ('(', '[', '{')
    right_brackets = (')', ']', '}')
    brackets = {
        "(": ")",
        "[": "]",
        "{": "}",
        ")": "(",
        "]": "[",
        "}": "{"
    }
    threshold = 1000000

    def cover(self, left, right):
        return sublime.Region(left.a, right.b)

    def all_parents(self):
        pairs = []
        for region in self.view.sel():
            parents = self.parents(region.a, self.threshold)
            if parents:
                if pairs and parents == pairs[-1]:
                    continue
                else:
                    pairs.append(parents)
        return pairs

    # 以后考虑渐进增大搜索区域，不然对于大文件的编辑，
    # 即使光标置于空括号内部，也将会导致一定的延迟，鉴于人们一般不会对
    # 不再视界之内的内容进行操作，故此处搜做的范围平均来说不会超过10000，
    # 然而如下的一开始便对一个很大的范围进行 extract_tokens是很不合理的，
    # 这是对大文件使用这些命令，会导致延迟的一个重要原因
    def parents(self, point, threshold):
        begin = max(point - threshold//2, 0)
        end = min(begin + threshold, self.view.size())
        extract_tokens = self.view.extract_tokens_with_scopes
        ltokens = extract_tokens(sublime.Region(begin, point))
        rtokens = extract_tokens(sublime.Region(point, end))
        if ltokens and rtokens:
            if ltokens[-1] == rtokens[0]:
                ltokens.pop()
            begin = (ltokens if ltokens else rtokens)[0][0].a
            end = rtokens[-1][0].b
            contents = self.view.substr(sublime.Region(begin, end))

            stack = []
            ltokens.reverse()
            for region, scope in ltokens:
                token = contents[region.a - begin:region.b - begin]
                if token in self.brackets:
                    # skip ignore
                    if "comment" in scope or "string" in scope:
                        continue

                    if token in self.right_brackets:
                        stack.append(token)

                    elif stack:
                        if self.brackets[token] == stack[-1]:
                            stack.pop()
                        else:
                            return False
                    else:
                        left_region = region
                        left_parent = token

                        for region, scope in rtokens:
                            token = contents[region.a - begin:region.b - begin]
                            if token in self.brackets:
                                # skip ignore
                                if "comment" in scope or "string" in scope:
                                    continue

                                if token in self.left_brackets:
                                    stack.append(token)

                                elif stack:
                                    if self.brackets[token] == stack[-1]:
                                        stack.pop()
                                    else:
                                        return False

                                elif self.brackets[left_parent] == token:
                                        return (left_region, region)

                                else:
                                    return False
        return False


class BracketsSelectorCommand(BracketsOperater):
    def run(self, edit):
        for p in self.all_parents():
            cover = self.cover(p[0], p[1])
            self.view.sel().add(cover)


class BracketsTransformCommand(BracketsOperater):
    def run(self, edit, to):
        for p in self.all_parents():
            if self.view.substr(p[0]) == to:
                continue
            self.view.replace(edit, p[0], to)
            self.view.replace(edit, p[1], self.brackets[to])


class BracketsTakeOffCommand(BracketsOperater):
    def run(self, edit):
        parents = [p for p in self.all_parents()]
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
