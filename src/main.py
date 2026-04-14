from zb_quotes.import_data.quote_importer import QuoteImporter
from zb_quotes.import_data.quote_importer_2 import QuoteImporter2

print("--------> It is ZbQuotes <--------")

# quote_importer = QuoteImporter()
quote_importer = QuoteImporter2()
quote_importer.import_quotes()
