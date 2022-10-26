from enum import Enum
from typing import NewType, List, Union

Template = NewType('RuntimeTemplate', List[Union[int, str, List]])


class GTMRootKeys(Enum):
    URL = 'https://www.googletagmanager.com/gtm.js?id='
    RESOURCE = 'resource'
    RUNTIME = 'runtime'
    PERMISSIONS = 'permissions'
    SANDBOXED_SCRIPTS = 'sandboxed_scripts'


class GTMResourceKeys(Enum):
    VERSION = 'version'
    MACROS = 'macros'
    TAGS = 'tags'
    PREDICATES = 'predicates'
    RULES = 'rules'


class UnaryOperator(Enum):
    logical_not = '!'
    negation = '-'
    bitwise_negation = '~'
    typeof = 'typeof'


class BinaryOperator(Enum):
    addition = '+'
    logical_and = '&&'
    assignment = '='
    division = '/'
    equality = '=='
    greater_than = '>'
    greater_than_equal_to = '>='
    strict_equality = '==='
    strict_inequality = '!=='
    less_than = '<'
    less_than_equal_to = '<='
    remainder = '%'
    multiplication = '*'
    inequality = '!='
    logical_or = '||'
    bitwise_and = '&'
    bitwise_leftshift = '<<'
    bitwise_or = '|'
    bitwise_rightshift = '>>'
    bitwise_unsigned_rightshift = '>>>'
    bitwise_xor = '^'


class TernaryOperator(Enum):
    ternary_operator = '?'


class Statement(Enum):
    return_statement = 'return'
    null = 'null'
    for_statement = 'for'
    if_statement = 'if'
    break_statement = 'break'
    continue_statement = 'continue'
    undefined = 'undefined'
    default = 'default'
    case = 'case'
    switch = 'switch'
    while_statement = 'while'
    function = 'function'
    control = 'control'


class ValueStatement(Enum):
    var = 'var'
    let = 'let'
    const = 'const'


class PropertyAccessor(Enum):
    brackets = '[]'
    dot = '.'


class PropertySetter(Enum):
    brackets = '[]'


class Array(Enum):
    index_based = '[]'
    key_value_based = '{}'


skip_macro_keys = ['title', 'isBuiltin', 'pill', 'nameProperty', 'function', 'infoKey']
skip_tag_keys = ['pill', 'property', 'nameProperty', 'title', 'function', 'infoKey', 'teardown_tags',
                 'setup_tags', '_sequence', '_conditions', '_blocking', 'exportType']
skip_trigger_keys = ['gtm.triggerGroup', '__tg']
triggers_not_tags = ['__tl', '__tg', '__cl', '__lcl', '__evl']
code_snippet_properties = ['vtp_html', 'vtp_javascript']
untracked_macros = ['Environment name']
runtime_function_regex = [r'__cvt_\d+_\d+', r'__awec', r'__baut', r'__crto', r'__pntr']

tags_index = {
    '__paused': {
        'title': 'Paused Tag',
        'nameProperty': 'vtp_originalTagType',
        'pill': 'light'
    },
    '__abtGeneric': {'title': 'AB TASTY Generic Tag'},
    '__adm': {'title': 'Adometry Tag'},
    '__asp': {'title': 'AdRoll Smart Pixel Tag'},
    '__awct': {'title': 'Google Ads Conversion Tracking Tag'},
    '__sp': {'title': 'Google Ads Remarketing Tag'},
    '__awc': {'title': 'Affiliate Window Conversion Tag'},
    '__awj': {'title': 'Affiliate Window Journey Tag'},
    '__baut': {'title': 'Bing Ads Universal Event Tracking'},
    '__bb': {'title': 'Bizrate Insights Buyer Survey Solution'},
    '__bsa': {'title': 'Bizrate Insights Site Abandonment Survey Solution'},
    '__cts': {'title': 'ClickTale Standard Tracking Tag'},
    '__csm': {'title': 'comScore Unified Digital Measurement Tag'},
    '__gclidw': {'title': 'Conversion Linker'},
    '__cegg': {'title': 'Crazy Egg Tag'},
    '__crto': {'title': 'Criteo OneTag'},
    '__html': {
        'title': 'Custom HTML Tag',
        'infoKey': 'vtp_html'
    },
    '__img': {'title': 'Custom Image Tag'},
    '__dstag': {'title': 'DistroScale Tag'},
    '__flc': {'title': 'Floodlight Counter Tag'},
    '__fls': {'title': 'Floodlight Sales Tag'},
    '__m6d': {'title': 'Dstillery Universal Pixel Tag'},
    '__ela': {'title': 'Eulerian Analytics Tag'},
    '__ga': {
        'title': 'Google Analytics Tag',
        'pill': 'warning'
    },
    '__gcs': {'title': 'Google Consumer Surveys Website Satisfaction'},
    '__opt': {'title': 'Google Optimize'},
    '__ts': {'title': 'Google Trusted Stores Tag'},
    '__hjtc': {
        'title': 'Hotjar Tracking Code',
        'pill': 'danger'
    },
    '__infinity': {'title': 'Infinity Call Tracking Tag'},
    '__sca': {'title': 'Intent Media - Search Compare Ads'},
    '__k50Init': {'title': 'K50 tracking tag'},
    '__ll': {'title': 'LeadLab'},
    '__bzi': {'title': 'LinkedIn Tag'},
    '__ljs': {'title': 'Lytics JS Tag'},
    '__ms': {'title': 'Marin Software Tag'},
    '__mpm': {'title': 'Mediaplex - IFRAME MCT Tag'},
    '__mpr': {'title': 'Mediaplex - Standard IMG ROI Tag'},
    '__mf': {'title': 'Mouseflow Tag'},
    '__ndcr': {'title': 'Nielsen DCR Static Lite Tag'},
    '__nudge': {'title': 'Nudge Content Analytics Tag'},
    '__okt': {'title': 'Oktopost Tracking Code'},
    '__omc': {'title': 'Optimise Conversion Tag'},
    '__messagemate': {'title': 'OwnerListens Message Mate'},
    '__pa': {'title': 'Perfect Audience Pixel'},
    '__pc': {'title': 'Personali Canvas'},
    '__placedPixel': {'title': 'Placed'},
    '__pijs': {'title': 'Pulse Insights Voice of Customer Platform'},
    '__qcm': {'title': 'Quantcast Audience Measurement'},
    '__fxm': {'title': 'Rawsoft FoxMetrics'},
    '__scjs': {'title': 'SaleCycle JavaScript Tag'},
    '__scp': {'title': 'SaleCycle Pixel Tag'},
    '__sfc': {'title': 'SearchForce JavaScript Tracking for Conversion Page'},
    '__sfl': {'title': 'SearchForce JavaScript Tracking for Landing Page'},
    '__sfr': {'title': 'SearchForce Redirection Tracking Tag'},
    '__shareaholic': {'title': 'Shareaholic'},
    '__svw': {'title': 'Survicate Widget'},
    '__tdlc': {'title': 'Tradedoubler Lead Conversion Tag'},
    '__tdsc': {'title': 'Tradedoubler Sale Conversion Tag'},
    '__tc': {'title': 'Turn Conversion Tracking Tag'},
    '__tdc': {'title': 'Turn Data Collection Tag'},
    '__twitter_website_tag': {'title': 'Twitter Universal Website Tag'},
    '__ua':
        {'title': 'Universal Analytics Tag',
         'nameProperty': 'vtp_trackType',
         'pill': 'warning'
         },
    '__uslt': {'title': 'Upsellit Global Footer Tag'},
    '__uspt': {'title': 'Upsellit Confirmation Tag'},
    '__vei': {'title': 'Ve Interactive JavaScript Tag'},
    '__veip': {'title': 'Ve Interactive Pixel'},
    '__vdc': {'title': 'VisualDNA Conversion Tag'},
    '__xpsh': {'title': 'Xtremepush'},
    '__yieldify': {'title': 'Yieldify'},
    '__qpx': {'title': 'Quora'},
    '__pntr': {'title': 'Pinterest'},
    '__gaawc': {'title': 'GA4 Configuration', 'pill': 'warning'},
    '__gaawe': {'title': 'GA4 Event', 'pill': 'warning', 'nameProperty': 'vtp_eventName'},
    '_custom_tag_template': {'title': 'Custom Tag Template', 'pill': 'dark', 'nameProperty': 'function'},
    '__ac360': {'title': 'Audience Center 360'},
    '__awcc': {'title': 'Google Ads Calls from Website Conversion', 'pill': 'primary',
               'nameProperty': 'vtp_phoneConversionNumber'},
    '__awud': {'title': 'Google Ads User-provided Data Event', 'pill': 'primary'},
    '__cloud_retail': {'title': 'Google Cloud Retail'},
    '__automl': {'title': 'Google Cloud Recommendations AI'},
    '__gfct': {'title': 'Google Flights Conversion Tracking'},
    '__gfpa': {'title': 'Google Flights Price Accuracy'},
    '__ta': {'title': 'Neustar AdAdvisor'},
    '__qca': {'title': 'Quantcast Advertise'},
    '__tpdpx': {'title': 'Tapad Conversion Pixel'}
}

macros_index = {
    '__k': {'title': 'First Party Cookie', 'nameProperty': 'vtp_name'},
    '__c': {'title': 'Constant', 'nameProperty': 'vtp_value'},
    '__ctv': {'title': 'Container Version', 'isBuiltIn': not False, 'pill': 'primary'},
    '__e': {'title': 'Event', 'isBuiltIn': not False, 'pill': 'primary'},
    '__jsm': {'title': 'Custom JavaScript Variable', 'infoKey': 'vtp_javascript'},
    '__v': {'title': 'Data Layer Var', 'nameProperty': 'vtp_name', 'pill': 'primary'},
    '__dbg': {'title': 'Debug Mode', 'isBuiltIn': not False, 'pill': 'primary'},
    '__d': {'title': 'DOM Element', 'nameProperty': 'vtp_selectorType'},
    '__vis': {'title': 'Element Visibility'},
    '__f': {'title': 'HTTP Referrer', 'nameProperty': 'vtp_component'},
    '__j': {'title': 'Global JavaScript Variable', 'nameProperty': 'vtp_name'},
    '__smm': {'title': 'Lookup Table'},
    '__r': {'title': 'Random Number', 'isBuiltIn': not False, 'pill': 'primary'},
    '__remm': {'title': 'RegEx Table'},
    '__u': {'title': 'URL', 'nameProperty': 'vtp_component'},
    '__gas': {'title': 'Google Analytics Settings', 'pill': 'warning'},
    '__aev': {'title': 'Auto Event Variable', 'nameProperty': 'vtp_varType', 'pill': 'primary'},
    '__cid': {'title': 'Container ID', 'pill': 'primary', 'isBuiltIn': not False},
    '__awec': {'title': 'User-Provided Data', 'pill': 'primary'},
    '_custom_variable_template': {'title': 'Custom Variable Template', 'pill': 'dark'},
    '__t': {'title': 'Custom Firing Schedule Enabled'},
    '__hid': {'title': 'HTML ID', 'isBuiltIn': not False},
    '__uv': {'title': 'Undefined Value', 'pill': 'dark'}
}

triggers_index = {
    '__evl': {'title': "Element Visibility", 'pill': "primary", 'exportType': "ELEMENT_VISIBILITY"},
    '__cl': {'title': "Click", 'pill': "primary", 'exportType': "CLICK"},
    '__fsl': {'title': "Form Submit", 'pill': "primary", 'exportType': "FORM_SUBMISSION"},
    '__hl': {'title': "History Listener", 'pill': "primary", 'exportType': "HISTORY_CHANGE"},
    '__jel': {'title': "JavaScript Error", 'pill': "primary", 'exportType': "JS_ERROR"},
    '__lcl': {'title': "Link Click", 'pill': "primary", 'exportType': "LINK_CLICK"},
    '__sdl': {'title': "Scroll Depth Listener", 'pill': "primary", 'exportType': "SCROLL_DEPTH"},
    '__tl': {'title': "Timer", 'pill': "primary", 'exportType': "TIMER"},
    '__ytl': {'title': "YouTube Video Listener", 'pill': "primary", 'exportType': "YOU_TUBE_VIDEO"},
    "gtm.dom": {'title': "DOM Ready", 'pill': "primary", 'exportType': "DOM_READY"},
    "gtm.load": {'title': "Window Loaded", 'pill': "primary", 'exportType': "WINDOW_LOADED"},
    "gtm.js": {'title': "Page View", 'pill': "primary", 'exportType': "PAGEVIEW"},
    "gtm.click": {'title': "Click", 'pill': "primary", 'exportType': "CLICK"},
    "gtm.triggerGroup": {'title': "Trigger Group", 'pill': "secondary", 'exportType': "TRIGGER_GROUP"},
    "gtm.historyChange": {'title': "History Change", 'pill': "secondary", 'exportType': "HISTORY_CHANGE"},
    '__e': {'title': "Custom Event", 'pill': "warning", 'exportType': "CUSTOM_EVENT"},
    '__tg': {'title': "Trigger Group", 'pill': "secondary", 'exportType': "TRIGGER_GROUP"},
    'gtm.init_consent': {'title': 'Consent Initialization', 'pill': 'primary', 'exportType': "CONSENT INITIALIZATION"},
    'gtm.init': {'title': 'Initialization', 'pill': 'primary', 'exportType': "INITIALIZATION"}
}

evaluations_index = {
    '_cn': {'title': "contains", 'exportTitle': "CONTAINS"},
    '_css': {'title': "matches css selector", 'exportTitle': "CSS_SELECTOR'"},
    '_ew': {'title': "ends with", 'exportTitle': "ENDS_WITH'"},
    '_eq': {'title': "equals", 'exportTitle': "EQUALS"},
    '_ge': {'title': ">=", 'exportTitle': "GREATER_OR_EQUALS'"},
    '_gt': {'title': ">", 'exportTitle': "GREATER"},
    '_le': {'title': "<=", 'exportTitle': "LESS_OR_EQUALS'"},
    '_lt': {'title': "<", 'exportTitle': "LESS"},
    '_lc': {'title': "later"},
    '_re': {'title': "matches regex", 'exportTitle': "MATCH_REGEX'"},
    '_sw': {'title': "starts with", 'exportTitle': "STARTS_WITH'"},
    '_um': {'title': "url matches", 'exportTitle': "URL_MATCHES'"}
}

dlvBuiltins_index = {
    "gtm.element": {'title': "Click Element"},
    "gtm.elementClasses": {'title': "Click Classes"},
    "gtm.elementId": {'title': "Click ID"},
    "gtm.elementTarget": {'title': "Click Target"},
    "gtm.elementUrl": {'title': "Click URL"},
    "gtm.elementText": {'title': "Click Text"},
    "gtm.errorMessage": {'title': "Error Message"},
    "gtm.errorUrl": {'title': "Error URL"},
    "gtm.errorLineNumber": {'title': "Error Line"},
    "gtm.historyChangeSource": {'title': "History Source"},
    "gtm.newUrlFragment": {'title': "New History Fragment"},
    "gtm.newHistoryState": {'title': "New History State"},
    "gtm.oldUrlFragment": {'title': "Old History Fragment"},
    "gtm.oldHistoryState": {'title': "Old History State"},
    "gtm.scrollThreshold": {'title': "Scroll Depth Threshold"},
    "gtm.scrollUnits": {'title': "Scroll Depth Units"},
    "gtm.scrollDirection": {'title': "Scroll Depth Direction"},
    "gtm.videoCurrentTime": {'title': "Video Current Time"},
    "gtm.videoDuration": {'title': "Video Duration"},
    "gtm.videoPercent": {'title': "Video Percent"},
    "gtm.videoProvider": {'title': "Video Provider"},
    "gtm.videoStatus": {'title': "Video Status"},
    "gtm.videoTitle": {'title': "Video Title"},
    "gtm.videoUrl": {'title': "Video URL"},
    "gtm.videoVisible": {'title': "Video Visible"},
    "gtm.visibleRatio": {'title': "Element Visibility Ratio (Percent Visible)"},
    "gtm.visibleTime": {'title': "Element Visibility Time (On-Screen Duration)"}
}

runtime_index = {
    0: {'symbol': '+',
        'type': BinaryOperator,
        'name': 'addition',
        'method': 'parse_binary_operator'},  # DONE
    1: {'symbol': '&&',
        'type': BinaryOperator,
        'name': 'logical AND',
        'method': 'parse_binary_operator'},  # DONE
    2: {'symbol': '.',
        'type': PropertyAccessor,
        'name': 'method accessor', 'method': 'parse_method_accessor'},  # DONE
    3: {'symbol': '=',
        'type': BinaryOperator,
        'name': 'assignment', 'method': 'parse_binary_operator'},  # DONE
    4: {'symbol': 'break',
        'type': Statement,
        'name': 'break statement', 'method': 'parse_simple_statement'},  # DONE
    5: {'symbol': 'case',
        'type': Statement,
        'name': 'case (switch)', 'method': 'parse_switch_expressions'},  # DONE
    6: {'symbol': 'continue',
        'type': Statement,
        'name': 'continue statement',
        'method': 'parse_simple_statement'},  # DONE
    7: {'symbol': '[]',
        'type': Array,
        'name': 'index based array', 'method': 'parse_array_literal'},  # DONE
    8: {'symbol': '{}',
        'type': Array,
        'name': 'key-value based array', 'method': 'parse_key_value_object'},  # DONE
    9: {'symbol': 'default',
        'type': Statement,
        'name': 'default (switch)',
        'method': 'parse_switch_expressions'},  # DONE
    10: {'symbol': '/',
         'type': BinaryOperator,
         'name': 'division', 'method': 'parse_binary_operator'},  # DONE
    11: {'symbol': '[]',
         'type': '',
         'name': ''},  # EMPTY
    12: {'symbol': '==',
         'type': BinaryOperator,
         'name': 'equality', 'method': 'parse_binary_operator'},  # DONE
    13: {'symbol': '[]',
         'type': '',
         'name': '', 'method': 'parse_return_multiple'},  # DONE
    14: {'symbol': '[]',
         'type': '',
         'name': ''},  # EMPTY
    15: {'symbol': 'variable_reference',
         'type': '',
         'name': '', 'method': 'parse_value_reference'},  # DONE
    16: {'symbol': '[]',
         'type': PropertyAccessor,
         'name': 'property accessor',
         'method': 'parse_property_accessor'},  # DONE
    17: {'symbol': '.',
         'type': PropertyAccessor,
         'name': 'property accessor',
         'method': 'parse_binary_operator'},  # DONE
    18: {'symbol': '>',
         'type': BinaryOperator,
         'name': 'larger than', 'method': 'parse_binary_operator'},  # DONE
    19: {'symbol': '>=',
         'type': BinaryOperator,
         'name': 'larger than or equal to',
         'method': 'parse_binary_operator'},  # DONE
    20: {'symbol': '===',
         'type': BinaryOperator,
         'name': 'equality with type comparison',
         'method': 'parse_binary_operator'},  # DONE
    21: {'symbol': '!==',
         'type': BinaryOperator,
         'name': 'NOT equality with type comparison',
         'method': 'parse_binary_operator'},  # DONE
    22: {'symbol': 'if',
         'type': Statement,
         'name': 'if statement',
         'method': 'parse_if_statement'},  # DONE
    23: {'symbol': '<',
         'type': BinaryOperator,
         'name': 'less than', 'method': 'parse_binary_operator'},  # DONE
    24: {'symbol': '<=',
         'type': BinaryOperator,
         'name': 'less than or equal to',
         'method': 'parse_binary_operator'},  # DONE
    25: {'symbol': '%',
         'type': BinaryOperator,
         'name': 'division reminder',
         'method': 'parse_binary_operator'},  # DONE
    26: {'symbol': '*',
         'type': BinaryOperator,
         'name': 'multiplication', 'method': 'parse_binary_operator'},  # DONE
    27: {'symbol': '-',
         'type': UnaryOperator,
         'name': 'unary negation', 'method': 'parse_unary_operator'},  # DONE
    28: {'symbol': '!',
         'type': UnaryOperator,
         'name': 'logical NOT', 'method': 'parse_unary_operator'},  # DONE
    29: {'symbol': '!=',
         'type': BinaryOperator,
         'name': 'NOT equality', 'method': 'parse_binary_operator'},  # DONE
    30: {'symbol': '||',
         'type': BinaryOperator,
         'name': 'logical OR', 'method': 'parse_binary_operator'},  # DONE
    31: {'symbol': '[]',
         'type': '',
         'name': ''},  # EMPTY
    32: {'symbol': '--',
         'type': UnaryOperator,
         'name': 'decrement',
         'method': 'parse_unary_operator',
         'variation': 'postfix'},  # DONE
    33: {'symbol': '++',
         'type': UnaryOperator,
         'name': 'increment',
         'method': 'parse_unary_operator',
         'variation': 'postfix'},  # DONE
    34: {'symbol': '--',
         'type': UnaryOperator,
         'name': 'decrement',
         'method': 'parse_unary_operator',
         'variation': 'prefix'},  # DONE
    35: {'symbol': '++',
         'type': UnaryOperator,
         'name': 'increment',
         'method': 'parse_unary_operator',
         'variation': 'prefix'},  # DONE
    36: {'symbol': 'return',
         'type': Statement,
         'name': 'return statement', 'method': 'parse_return_statement'},  # DONE
    37: {'symbol': '-',
         'type': BinaryOperator,
         'name': 'substraction', 'method': 'parse_binary_operator'},  # DONE
    38: {'symbol': 'switch',
         'type': Statement,
         'name': 'switch statement', 'method': 'parse_switch_statement'},  # DONE
    39: {'symbol': '?',
         'type': TernaryOperator,
         'name': 'ternary operator',
         'method': 'parse_ternary_operator'},  # DONE
    40: {'symbol': 'typeof',
         'type': UnaryOperator,
         'name': 'Type return operator',
         'method': 'parse_unary_operator'},  # DONE
    41: {'symbol': 'var',
         'type': ValueStatement,
         'name': 'variable declaration var/let',
         'variations': {1: 'var list', 2: 'let list'}, 'method': 'parse_let_const'},  # DONE
    42: {'symbol': 'while',
         'type': Statement,
         'name': 'while and do...while statement',
         'variations': {1: 'while', 2: 'do...while'},
         'method': 'parse_while_var_for_statement'},  # DONE
    43: {'symbol': '[]',
         'type': PropertySetter,
         'name': 'Property setter',
         'method': 'parse_property_setter'},  # DONE
    44: {'symbol': 'undefined',
         'type': Statement,
         'name': 'undefined statement',
         'method': 'parse_simple_statement'},  # DONE
    45: {'symbol':
             'null',
         'type': Statement,
         'name':
             'null type', 'method': 'parse_simple_statement'},  # DONE
    46: {'symbol': '[]',
         'type': '',
         'name': '', 'method': 'get_arguments'},  # DONE
    47: {'symbol': 'for',
         'type': Statement,
         'name': 'for statement',
         'variation': 'for (var a in b)',
         'method': 'parse_for_a_of_in_b'},  # DONE
    48: {'symbol': '[]',
         'type': '',
         'name': ''},  # EMPTY
    49: {'symbol': 'control',
         'type': Statement,
         'name': 'control statement',
         'method': 'parse_simple_statement'},  # DONE
    50: {'symbol': 'function',
         'type': Statement,
         'name': 'function',
         'variation': 'function definition', 'method': 'parse_defined_function'},  # WIP
    51: {'symbol': 'function',
         'type': Statement,
         'name': 'function',
         'variation': 'function assignment',
         'method': 'parse_assigned_function'},  # DONE
    52: {'symbol': 'const',
         'type': ValueStatement,
         'name': 'constant declaration',
         'method': 'parse_let_const'},  # DONE
    53: {'symbol': 'for',
         'type': Statement,
         'name': 'for statement',
         'variation': 'standard',
         'method': 'parse_standard_let_for_loop'},  # DONE - check parse_if_statement - 53 is not what is seems
    54: {'symbol': '[]',
         'type': '',
         'name': ''},  # EMPTY
    55: {'symbol': 'for',
         'type': Statement,
         'name': 'for statement',
         'variation': 'for (let a in b)',
         'method': 'parse_for_a_of_in_b'},  # DONE
    56: {'symbol': '&',
         'type': BinaryOperator,
         'name': 'Bitwise AND', 'method': 'parse_binary_operator'},  # DONE
    57: {'symbol': '<<',
         'type': BinaryOperator,
         'name': 'Bitwise Leftshift',
         'method': 'parse_binary_operator'},  # DONE
    58: {'symbol': '~',
         'type': UnaryOperator,
         'name': 'Bitwise negation', 'method': 'parse_unary_operator'},  # DONE
    59: {'symbol': '|',
         'type': BinaryOperator,
         'name': 'Bitwise OR', 'method': 'parse_binary_operator'},  # DONE
    60: {'symbol': '>>',
         'type': BinaryOperator,
         'name': 'Bitwise rightshift',
         'method': 'parse_binary_operator'},  # DONE
    61: {'symbol': '>>>',
         'type': BinaryOperator,
         'name': 'Unsigned Bitwise rightshift',
         'method': 'parse_binary_operator'},  # DONE
    62: {'symbol': '^',
         'type': BinaryOperator,
         'name': 'Bitwise XOR', 'method': 'parse_binary_operator'},  # DONE
    63: {'symbol': '[]',
         'type': '',
         'name': 'for_loop_body',
         'method': 'parse_for_loop_body'},  # DONE
    64: {'symbol': 'for',
         'type': Statement,
         'name': 'for statement',
         'variation': 'for (var a of b)',
         'method': 'parse_for_a_of_in_b'},  # DONE
    65: {'symbol': '[]',
         'type': '',
         'name': ''},  # EMPTY
    66: {'symbol': 'for',
         'type': Statement,
         'name': 'for statement',
         'variation': 'for (let a of b)',
         'method': 'parse_for_a_of_in_b'},  # DONE
    'require': {'symbol': '',
                'type': '',
                'name': 'require function', 'method': 'parse_require_exception'}
}
