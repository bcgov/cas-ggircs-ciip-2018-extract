import hashlib
import dateutil.parser
import datetime
import ntpath
from model.application import Application
import util
from util import get_sheet_value, search_row_index

def extract(ciip_book, book_path, facility):
    hasher = hashlib.sha1()
    with open(book_path, 'rb') as afile:
        buf = afile.read()
        hasher.update(buf)

    cert_sheet = ciip_book.sheet_by_name('Statement of Certification')
    co_header_idx = search_row_index(cert_sheet, 1, 'Signature of Certifying Official')
    if co_header_idx == -1:
        raise "could not find certyfing official header"

    signature_date = get_sheet_value(cert_sheet, co_header_idx + 7, 6)
    signature_date = dateutil.parser.parse(signature_date) if isinstance(signature_date, str) else None
    application_type = 'SFO' if 'Production' in ciip_book.sheet_names() else 'LFO'

    application = Application(
                        facility,
                        ntpath.basename(book_path),
                        hasher.hexdigest(),
                        datetime.datetime.now(),
                        2018,
                        application_type,
                        signature_date
                    )

    return application
