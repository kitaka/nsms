from django.test import TestCase
from .parser import Parser
import datetime

class ParserTest(TestCase):

    def assertNextWord(self, truth, sms, *args):
        # parser with delimiter
        parser = Parser(sms, *args)
        self.assertEquals(truth, parser.next_word())

    def test_word_parsing(self):
        self.assertNextWord("reg", "reg bach")
        self.assertNextWord("reg", "reg, bach", ',')
        self.assertNextWord("reg", "reg. bach", '.')

        self.assertNextWord("reg", "reg, bach", ' ',',', '.')
        self.assertNextWord("reg", "reg. bach", ' ',',', '.')
        self.assertNextWord("reg", "reg, bach", '.',',', ' ')
        self.assertNextWord("reg", "reg, bach", ',',' ', '.')

        self.assertNextWord("reg", "reg.bach", ' ',',', '.')
        self.assertNextWord("reg", "reg.,bach", ' ',',', '.')
        self.assertNextWord("reg", "reg..bach", ' ',',', '.')
        self.assertNextWord("reg", "reg,bach", ' ',',', '.')

        self.assertNextWord("reg", "reg mozart")
        self.assertNextWord("reg", "reg, mozart", ',')
        self.assertNextWord("reg", "reg. mozart", '.')

        self.assertNextWord("r", "r handell")
        self.assertNextWord("r", "r, handell", ',')
        self.assertNextWord("r", "r. handell", '.')

        self.assertNextWord(None, ", ", ',')
        self.assertNextWord(None, ". ", '.')

        self.assertNextWord(None, " ", ',',' ', '.')
        self.assertNextWord(None, ",", ',',' ', '.')
        self.assertNextWord(None, ", ", ',',' ', '.')
        self.assertNextWord(None, ".", ',',' ', '.')
        self.assertNextWord(None, ". ", ',',' ', '.')
        self.assertNextWord(None, ", . ,, ", ',',' ', '.')
        self.assertNextWord(None, " ...", ',',' ', '.')
        self.assertNextWord(None, ",., ", ',',' ', '.')
        self.assertNextWord(None, " ..,, ..,,", ',',' ', '.')
        self.assertNextWord(None, ",.,. ,.,. ", ',',' ', '.')

        self.assertNextWord("..", "..")
        self.assertNextWord(None, "  ")

        self.assertNextWord("..", "..", ',')
        self.assertNextWord(None, ",,", ',')

        self.assertNextWord(",,", ",,", '.')
        self.assertNextWord(None, "..", '.')

    def assertNextKeyword(self, truth, sms, keywords, *args):
        parser = Parser(sms, *args)
        self.assertEquals(truth, parser.next_keyword(keywords))

    def test_keyword_parsing(self):
        KEYWORDS = ["register", "reg"]

        self.assertNextKeyword("reg", "reg bach", KEYWORDS)
        self.assertNextKeyword("reg", "reg, bach", KEYWORDS, ',')
        self.assertNextKeyword("reg", "reg. bach", KEYWORDS, '.')

        self.assertNextKeyword("reg", "reg bach", KEYWORDS, '.', ' ', ',')
        self.assertNextKeyword("reg", "reg. bach", KEYWORDS, '.', ' ', ',')
        self.assertNextKeyword("reg", "reg, bach", KEYWORDS, '.', ' ', ',')

        self.assertNextKeyword("register", "register bach", KEYWORDS)
        self.assertNextKeyword("register", "register, bach", KEYWORDS, ',')
        self.assertNextKeyword("register", "register. bach", KEYWORDS, '.')

        self.assertNextKeyword("register", "register. bach", KEYWORDS, '.', ' ', ',')
        self.assertNextKeyword("register", "register bach", KEYWORDS, '.', ' ', ',')
        self.assertNextKeyword("register", "register, bach", KEYWORDS, '.', ' ', ',')

        self.assertNextKeyword("reg", "REG bach", KEYWORDS)
        self.assertNextKeyword("reg", "REG, bach", KEYWORDS, ',')
        self.assertNextKeyword("reg", "REG. bach", KEYWORDS, '.')

        self.assertNextKeyword(None, "notkeyword bach", KEYWORDS)
        self.assertNextKeyword(None, "notkeyword, bach", KEYWORDS, ',')
        self.assertNextKeyword(None, "notkeyword. bach", KEYWORDS, '.')

        self.assertNextKeyword(None, "notkeyword. bach", KEYWORDS, '.', ' ', ',')
        self.assertNextKeyword(None, "notkeyword bach", KEYWORDS, '.', ' ', ',')
        self.assertNextKeyword(None, "notkeyword, bach", KEYWORDS, '.', ' ', ',')

        self.assertNextKeyword(None, " ", KEYWORDS)
        self.assertNextKeyword(None, ",", KEYWORDS, ',')
        self.assertNextKeyword(None, ".", KEYWORDS, '.')

        self.assertNextKeyword(None, " ", KEYWORDS, ',', ' ', '.')
        self.assertNextKeyword(None, ",", KEYWORDS, ',', ' ', '.')
        self.assertNextKeyword(None, ".", KEYWORDS, '.', ' ', '.')

    def assertNextHour(self, truth, sms, *args):
        parser = Parser(sms, *args)
        self.assertEquals(truth, parser.next_hour())

    def test_hour_parsing(self):
        self.assertNextHour(12, " 1245 CET")
        self.assertNextHour(12, " 1245, CET", ',')
        self.assertNextHour(12, " 1245. CET", '.')

        # for anything number "l" should be treated like 1
        self.assertNextHour(12, " l245")

        # change "o" or "O" to be 0 as we expect only numbers
        self.assertNextHour(20, " 2o45")
        self.assertNextHour(20, " 2O45")

    def assertNextPhone(self, truth, sms, *args):
        parser = Parser(sms, *args)
        self.assertEquals(truth, parser.next_phone())

    def test_phone_parsing(self):
        self.assertNextPhone("0788383388", "  0788383388 Bach")
        self.assertNextPhone("0788383388", "  0788383388, Bach", ',')
        self.assertNextPhone("0788383388", "  0788383388. Bach", '.')

        self.assertNextPhone("0788383388", "  0788383388. Bach", '.', ' ', ',')
        self.assertNextPhone("0788383388", "  0788383388 Bach", '.', ' ', ',')
        self.assertNextPhone("0788383388", "  0788383388, Bach", '.', ' ', ',')

        self.assertNextPhone("250788383388", "  250788383388")
        self.assertNextPhone("250788383388", "  250788383388", ',')
        self.assertNextPhone("250788383388", "  250788383388", '.')

        self.assertNextPhone("250788383388", "  250788383388", '.', ' ', ',')
        self.assertNextPhone("250788383388", "  250788383388", '.', ' ', ',')
        self.assertNextPhone("250788383388", "  250788383388", '.', ' ', ',')

        self.assertNextPhone("250788383388", " +250788383388")
        self.assertNextPhone("250788383388", " +250788383388", ',')
        self.assertNextPhone("250788383388", " +250788383388", '.')

        self.assertNextPhone("250788383388", " +250788383388", '.', ' ', ',')
        self.assertNextPhone("250788383388", " +250788383388", '.', ' ', ',')
        self.assertNextPhone("250788383388", " +250788383388", '.', ' ', ',')

        # for anything number "l" should be treated like 1
        self.assertNextPhone("250788183388", " 250788l83388")

        # change "o" or "O" to be 0 as we expect only numbers
        self.assertNextPhone("250788310338", " 2507883lo338")
        self.assertNextPhone("250788310338", " 2507883l0338")

        # nothing there
        self.assertNextPhone(None, " ")
        self.assertNextPhone(None, " ", ',')
        self.assertNextPhone(None, " ", '.')

        self.assertNextPhone(None, " ", '.', ' ', ',')
        self.assertNextPhone(None, " ", '.', ' ', ',')
        self.assertNextPhone(None, " ", '.', ' ', ',')

        # not numeric
        self.assertNextPhone(None, "078838338a")
        self.assertNextPhone(None, "078838338a", ',')
        self.assertNextPhone(None, "078838338a", '.')

        # not correct length
        self.assertNextPhone(None, "07883833881")
        self.assertNextPhone(None, "07883833881", ',')
        self.assertNextPhone(None, "07883833881", '.')

        self.assertNextPhone(None, "07883833881", '.', ' ', ',')
        self.assertNextPhone(None, "07883833881", '.', ' ', ',')
        self.assertNextPhone(None, "07883833881", '.', ' ', ',')

    def assertNextInt(self, truth_int, sms, *args):
        parser = Parser(sms, *args)
        self.assertEquals(truth_int, parser.next_int())

    def test_int_parsing(self):
        self.assertNextInt('120', "  120 Homeless children")
        self.assertNextInt('120', "  120, Homeless children", ',')
        self.assertNextInt('120', "  120. Homeless children", '.')

        # resolve confused characters to number 'l', 'O' or 'o'
        self.assertNextInt('120', "  l20 Homeless children")
        self.assertNextInt('120', "  l2o Homeless children")
        self.assertNextInt('120', "  l2O Homeless children")

    def assertNextDate(self, truth_day, truth_month, truth_year, sms):
        parser = Parser(sms)
        truth = None

        if truth_day:
            truth = datetime.date(day=truth_day, month=truth_month, year=truth_year)

        self.assertEquals(truth, parser.next_date())

    def test_date_parsing(self):
        self.assertNextDate(23, 6, 1977, "23.6.77")
        self.assertNextDate(23, 6, 1977, "23/6/77")
        self.assertNextDate(23, 6, 1977, "23-6-77")

        self.assertNextDate(23, 6, 1977, "23.06.77")
        self.assertNextDate(23, 6, 1977, "23/06/77")
        self.assertNextDate(23, 6, 1977, "23-06-77")

        self.assertNextDate(23, 6, 2011, "23.06.11")
        self.assertNextDate(23, 6, 2011, "23/06/11")
        self.assertNextDate(23, 6, 2011, "23-06-11")

        self.assertNextDate(23, 6, 2000, "23.06.00")
        self.assertNextDate(23, 6, 2000, "23/06/00")
        self.assertNextDate(23, 6, 2000, "23-06-00")

        # invalid day
        self.assertNextDate(None, None, None, "31.6.77")
        self.assertNextDate(None, None, None, "31/6/77")
        self.assertNextDate(None, None, None, "31-6-77")

        # invalid month
        self.assertNextDate(None, None, None, "10.13.77")
        self.assertNextDate(None, None, None, "10/13/77")
        self.assertNextDate(None, None, None, "10-13-77")

        # invalid year
        self.assertNextDate(None, None, None, "10.13.113")
        self.assertNextDate(None, None, None, "10/13/113")
        self.assertNextDate(None, None, None, "10-13-113")

        # invalid format
        self.assertNextDate(None, None, None, "10 12 31")
        self.assertNextDate(None, None, None, "10;12;31")
        self.assertNextDate(None, None, None, "10:12:31")

    def assertWordCount(self, truth, sms, *args):
        parser = Parser(sms, *args)
        self.assertEquals(truth, parser.word_count)

    def test_word_count(self):
        self.assertWordCount(0, "  ")
        self.assertWordCount(0, "  ", ',')
        self.assertWordCount(0, ", ", ',')
        self.assertWordCount(0, "  ", '.')
        self.assertWordCount(0, ". ", '.')

        self.assertWordCount(0, "")
        self.assertWordCount(0, "", ',')
        self.assertWordCount(0, "", '.')

        self.assertWordCount(1, "  hello  ")
        self.assertWordCount(1, "  hello  ", ',')
        self.assertWordCount(1, "  hello  ", '.')

        self.assertWordCount(2, "  hello. world")
        self.assertWordCount(2, "  hello., world", ',')
        self.assertWordCount(2, "  hello,. world", '.')

        self.assertWordCount(2, " hello world.foo")
        self.assertWordCount(2, " hello, world.foo", ',')
        self.assertWordCount(2, " hello. world,foo", '.')

    def test_parsing(self):
        parser = Parser("REG James Kirk 10.12.44 0788383381")

        self.assertEquals("reg", parser.next_keyword(["reg"]))
        self.assertEquals("James", parser.next_word())
        self.assertEquals("Kirk", parser.next_word())
        self.assertEquals(datetime.date(day=10, month=12, year=1944), parser.next_date())
        self.assertEquals("0788383381", parser.next_phone())

        self.assertFalse(parser.has_word())

        parser = Parser("REG, James, Kirk, 10.12.44, 0788383381", ',')

        self.assertEquals("reg", parser.next_keyword(["reg"]))
        self.assertEquals("James", parser.next_word())
        self.assertEquals("Kirk", parser.next_word())
        self.assertEquals(datetime.date(day=10, month=12, year=1944), parser.next_date())
        self.assertEquals("0788383381", parser.next_phone())

        self.assertFalse(parser.has_word())

        parser = Parser("REG. James. Kirk. 10/12/44. 0788383381", '.')

        self.assertEquals("reg", parser.next_keyword(["reg"]))
        self.assertEquals("James", parser.next_word())
        self.assertEquals("Kirk", parser.next_word())
        self.assertEquals(datetime.date(day=10, month=12, year=1944), parser.next_date())
        self.assertEquals("0788383381", parser.next_phone())

        self.assertFalse(parser.has_word())

        parser = Parser("REG.James.Kirk.10/12/44.0788383381", '.')

        self.assertEquals("reg", parser.next_keyword(["reg"]))
        self.assertEquals("James", parser.next_word())
        self.assertEquals("Kirk", parser.next_word())
        self.assertEquals(datetime.date(day=10, month=12, year=1944), parser.next_date())
        self.assertEquals("0788383381", parser.next_phone())

        self.assertFalse(parser.has_word())

        parser = Parser("REG.James.Kirk.10/12/44.0788383381", '.', ' ', ',')

        self.assertEquals("reg", parser.next_keyword(["reg"]))
        self.assertEquals("James", parser.next_word())
        self.assertEquals("Kirk", parser.next_word())
        self.assertEquals(datetime.date(day=10, month=12, year=1944), parser.next_date())
        self.assertEquals("0788383381", parser.next_phone())

        self.assertFalse(parser.has_word())


        parser = Parser("REG.James,Kirk 10/12/44,0788383381", '.', ' ', ',')

        self.assertEquals("reg", parser.next_keyword(["reg"]))
        self.assertEquals("James", parser.next_word())
        self.assertEquals("Kirk", parser.next_word())
        self.assertEquals(datetime.date(day=10, month=12, year=1944), parser.next_date())
        self.assertEquals("0788383381", parser.next_phone())

        self.assertFalse(parser.has_word())

        parser = Parser("REG James,.Kirk, . 10/12/44,0788383381", '.', ' ', ',')

        self.assertEquals("reg", parser.next_keyword(["reg"]))
        self.assertEquals("James", parser.next_word())
        self.assertEquals("Kirk", parser.next_word())
        self.assertEquals(datetime.date(day=10, month=12, year=1944), parser.next_date())
        self.assertEquals("0788383381", parser.next_phone())

        self.assertFalse(parser.has_word())

