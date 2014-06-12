import text
from feed import FeedPoller

import re


class MinglePoller(FeedPoller):
    """
    Format changes to Mingle cards
    """
    def parse(self, entry):
        m = re.search(r'^(.*/([0-9]+))', entry.id)
        if not m:
            print "bad entry, %s" % (entry.id, )
            return None
        url = m.group(1)
        issue = int(m.group(2))
        author = text.abbrevs(entry.author_detail.name)

        assignments = []
        details = entry.content[0].value
        assignment_phrases = [
            r"""(?x)
                (?P<property> [^,>]+ )
                \s set \s to \s
                (?P<value> [^,<]+ \w )
            """,
            r"""(?x)
                (?P<property> [^,>]+ )
                \s changed \s from \s
                (?P<previous_value> [^,<]+ )
                \s to \s
                (?P<value> [^,<]+ \w )
            """,
        ]
        for pattern in assignment_phrases:
            for m in re.finditer(pattern, details):
                normal_form = None
                date_re = r'\d{4}/\d{2}/\d{2}|\(not set\)'
                if re.match(date_re, m.group('value')):
                    pass
                elif re.match(r'Planning - Sprint', m.group('property')):
                    n = re.search(r'(Sprint \d+)', m.group('value'))
                    if n:
                        normal_form = "->" + n.group(1)
                elif 'Deployed' == m.group('value'):
                    normal_form = "*Deployed*"
                else:
                    normal_form = text.abbrevs("{prop} : {value}".format(
                        prop=m.group('property'),
                        value=m.group('value')
                    ))

                if normal_form:
                    assignments.append(normal_form)
        summary = '|'.join(assignments)

        assignment_re = r'(?P<property>[^:>]+): (?P<value>[^<]+)'
        for m in re.finditer(assignment_re, details):
            if m.group('property') == 'Comment added':
                summary = m.group('value')+" "+summary
        for m in re.finditer(r'Description changed', details):
            summary += " " + m.group(0)

        summary = text.strip(summary, truncate=True)

        if summary:
            return "#%d: (%s) %s -- %s" % (issue, author, summary, url)
