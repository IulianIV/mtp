import re
from urllib.parse import quote, unquote, urlparse, parse_qs

from flask import (
    render_template, request
)

from app.auth.routes import login_required
from app.manager.db.db_interrogations import *
from app.manager.helpers import form_validated_message, form_error_message
from app.webtools import bp, forms

# TODO Add a UTM interpreter for in-database URLs and metric/statistics to that.
#   can and should be located in the reporting & statistics app and here only have a link to it.
# TODO automatically validate URLs as TRUE at column level "is_marketing" if it contains any UTM parameter.
#   if is_marketing, split and send to UTM analyzer.

encodings = ['ascii', 'big5', 'big5hkscs', 'cp037', 'cp273', 'cp424', 'cp437', 'cp500', 'cp720', 'cp737', 'cp775',
             'cp850', 'cp852', 'cp855', 'cp856', 'cp857', 'cp858', 'cp860', 'cp861', 'cp862', 'cp863', 'cp864',
             'cp865', 'cp866', 'cp869', 'cp874', 'cp875', 'cp932', 'cp949', 'cp950', 'cp1006', 'cp1026', 'cp1125',
             'cp1140', 'cp1250', 'cp1251', 'cp1252', 'cp1253', 'cp1254', 'cp1255', 'cp1256', 'cp1257', 'cp1258',
             'cp65001', 'euc_jp', 'euc_jis_2004', 'euc_jisx0213', 'euc_kr', 'gb2312', 'gbk', 'gb18030', 'hz',
             'iso2022_jp', 'iso2022_jp_1', 'iso2022_jp_2', 'iso2022_jp_2004', 'iso2022_jp_3', 'iso2022_jp_ext',
             'iso2022_kr', 'latin_1', 'iso8859_2', 'iso8859_3', 'iso8859_4', 'iso8859_5', 'iso8859_6', 'iso8859_7',
             'iso8859_8', 'iso8859_9', 'iso8859_10', 'iso8859_11', 'iso8859_13', 'iso8859_14', 'iso8859_15',
             'iso8859_16', 'johab', 'koi8_r', 'koi8_t', 'koi8_u', 'kz1048', 'mac_cyrillic', 'mac_greek', 'mac_iceland',
             'mac_latin2', 'mac_roman', 'mac_turkish', 'ptcp154', 'shift_jis', 'shift_jis_2004', 'shift_jisx0213',
             'utf_32', 'utf_32_be', 'utf_32_le', 'utf_16', 'utf_16_be', 'utf_16_le', 'utf_7', 'utf_8', 'utf_8_sig']


@bp.route('/url-encode-decode-parser', methods=('GET', 'POST'))
@login_required
def url_encode_decode_parse():

    coder_parser_form = forms.EncodeDecodeParse()
    validated = False
    result_url = ''
    url_value = ''
    error_string = '_#_'
    parsed_url = ''
    decoded_url_query = ''
    raw_url_query = ''

    coder_parser_form.select_encoding.choices = encodings

    if request.method == 'POST':
        if coder_parser_form.is_submitted() and coder_parser_form.encode_decode.data:

            url_field = coder_parser_form.url_field.data
            encode = coder_parser_form.encode.data
            decode = coder_parser_form.decode.data
            selected_encoding = coder_parser_form.select_encoding.data

            if encode and decode:
                form_error_message('You can`t encode and decode simultaneously.')
            elif not encode and not decode:
                form_error_message('You must check at least one option.')

            if encode:
                try:
                    url_value = quote(url_field, encoding=selected_encoding)
                except UnicodeEncodeError:
                    form_error_message(f'Your URL contains unsupported characters for {selected_encoding} encoding.')
                else:
                    validated = True
                    add_new_url(url_field, 'encode', selected_encoding)
                    db.session.commit()
                    form_validated_message('URL successfully encoded.')

            if decode:
                if selected_encoding == 'utf_8':
                    url_value = unquote(url_field, errors=error_string, encoding=selected_encoding)
                else:
                    url_value = unquote(url_field, encoding=selected_encoding)
                if re.match(error_string, url_value):
                    form_error_message('The decode encountered a UTF-8 error. All occurrences of "_#_" in your result '
                                       'represent characters that have thrown the error.')
                    validated = True
                    add_new_url(url_field, decode, selected_encoding)
                    db.session.commit()
                else:
                    form_validated_message('URL successfully decoded.')
                    validated = True
                    add_new_url(url_field, 'decode', selected_encoding)
                    db.session.commit()

        # TODO add advanced query parsing with the ability to choose encoding (from already existing form)
        #   keep_blank_values, strict_parsing, errors, max_num_fields and separator

        if coder_parser_form.is_submitted() and coder_parser_form.parse.data:

            url_to_split = coder_parser_form.url_field.data

            parsed_url = urlparse(url_to_split)

            decoded_url_query = unquote(parsed_url.query)

            raw_url_query = parse_qs(parsed_url.query)

            add_new_url(url_to_split, None, None)
            db.session.commit()

            form_validated_message('URL parsed successfully!')

        if validated:
            coder_parser_form.url_field.data = coder_parser_form.encode.data = coder_parser_form.decode.data = ''
            result_url = url_value

    return render_template('webtools/encode_decode_parse.html', coder_parser_form=coder_parser_form,
                           result_url=result_url, parsed_url=[parsed_url, decoded_url_query, raw_url_query])


# TODO will check a URL, return its HTTP response, generate a preview, read and print OpenGraph data and preview it
#   for multiple social media websites and print JSON-LD schema if present and the type of structured data it holds.
@bp.route('/url-checker', methods=('GET', 'POST'))
@login_required
def url_checker():

    return render_template('webtools/url_checker.html')

