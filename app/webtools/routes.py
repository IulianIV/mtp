from flask import (
    render_template, request
)
from urllib.parse import quote, unquote, urlparse, parse_qs
from app.auth.routes import login_required
from app.manager.protection import form_validated_message, form_error_message
from app.webtools import bp, forms
import re

# TODO Gather this data through a button actioned parse of the python website that handles this data.
#   the parsed data should be added to a encodings database and accessed from there.
#   URL example: https://docs.python.org/3.7/library/codecs.html#standard-encodings

# TODO add option to modify encoding at choice, otherwise it defaults to utf-8
# better-me improve code and functionality
# better-me add functionality to choose encoding for decode and encode
# better-me do a database integration to remember all used URLs, options selected and parameters found
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
                else:
                    form_validated_message('URL successfully decoded.')
                    validated = True

        # TODO add advanced query parsing with the ability to choose encoding (from already existing form)
        #   keep_blank_values, strict_parsing, errors, max_num_fields and separator

        if coder_parser_form.is_submitted() and coder_parser_form.parse.data:

            url_to_split = coder_parser_form.url_field.data

            parsed_url = urlparse(url_to_split)

            decoded_url_query = unquote(parsed_url.query)

            raw_url_query = parse_qs(parsed_url.query)

            form_validated_message('URL parsed successfully!')

        if validated:
            coder_parser_form.url_field.data = coder_parser_form.encode.data = coder_parser_form.decode.data = ''
            result_url = url_value

    return render_template('webtools/urltools.html', coder_parser_form=coder_parser_form,
                           result_url=result_url, parsed_url=[parsed_url, decoded_url_query, raw_url_query])
