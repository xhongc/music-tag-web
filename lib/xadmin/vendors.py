
vendors = {
    "bootstrap": {
        'js': {
            'dev': 'xadmin/vendor/bootstrap/js/bootstrap.js',
            'production': 'xadmin/vendor/bootstrap/js/bootstrap.min.js',
            'cdn': 'http://netdna.bootstrapcdn.com/twitter-bootstrap/2.3.1/js/bootstrap.min.js'
        },
        'css': {
            'dev': 'xadmin/vendor/bootstrap/css/bootstrap.css',
            'production': 'xadmin/vendor/bootstrap/css/bootstrap.css',
            'cdn': 'http://netdna.bootstrapcdn.com/twitter-bootstrap/2.3.1/css/bootstrap-combined.min.css'
        },
        'responsive': {'css':{
                'dev': 'xadmin/vendor/bootstrap/bootstrap-responsive.css',
                'production': 'xadmin/vendor/bootstrap/bootstrap-responsive.css'
            }}
    },
    'jquery': {
        "js": {
            'dev': 'xadmin/vendor/jquery/jquery.js',
            'production': 'xadmin/vendor/jquery/jquery.min.js',
        }
    },
    'jquery-ui-effect': {
        "js": {
            'dev': 'xadmin/vendor/jquery-ui/jquery.ui.effect.js',
            'production': 'xadmin/vendor/jquery-ui/jquery.ui.effect.min.js'
        }
    },
    'jquery-ui-sortable': {
        "js": {
            'dev': ['xadmin/vendor/jquery-ui/jquery.ui.core.js', 'xadmin/vendor/jquery-ui/jquery.ui.widget.js',
                    'xadmin/vendor/jquery-ui/jquery.ui.mouse.js', 'xadmin/vendor/jquery-ui/jquery.ui.sortable.js'],
            'production': ['xadmin/vendor/jquery-ui/jquery.ui.core.min.js', 'xadmin/vendor/jquery-ui/jquery.ui.widget.min.js',
                           'xadmin/vendor/jquery-ui/jquery.ui.mouse.min.js', 'xadmin/vendor/jquery-ui/jquery.ui.sortable.min.js']
        }
    },
    "font-awesome": {
        "css": {
            'dev': 'xadmin/vendor/font-awesome/css/font-awesome.css',
            'production': 'xadmin/vendor/font-awesome/css/font-awesome.min.css',
        }
    },
    "timepicker": {
        "css": {
            'dev': 'xadmin/vendor/bootstrap-timepicker/css/bootstrap-timepicker.css',
            'production': 'xadmin/vendor/bootstrap-timepicker/css/bootstrap-timepicker.min.css',
        },
        "js": {
            'dev': 'xadmin/vendor/bootstrap-timepicker/js/bootstrap-timepicker.js',
            'production': 'xadmin/vendor/bootstrap-timepicker/js/bootstrap-timepicker.min.js',
        }
    },
    "clockpicker": {
        "css": {
            'dev': 'xadmin/vendor/bootstrap-clockpicker/bootstrap-clockpicker.css',
            'production': 'xadmin/vendor/bootstrap-clockpicker/bootstrap-clockpicker.min.css',
        },
        "js": {
            'dev': 'xadmin/vendor/bootstrap-clockpicker/bootstrap-clockpicker.js',
            'production': 'xadmin/vendor/bootstrap-clockpicker/bootstrap-clockpicker.min.js',
        }
    },
    "datepicker": {
        "css": {
            'dev': 'xadmin/vendor/bootstrap-datepicker/css/datepicker.css'
        },
        "js": {
            'dev': 'xadmin/vendor/bootstrap-datepicker/js/bootstrap-datepicker.js',
        }
    },
    "flot": {
        "js": {
            'dev': ['xadmin/vendor/flot/jquery.flot.js', 'xadmin/vendor/flot/jquery.flot.pie.js', 'xadmin/vendor/flot/jquery.flot.time.js',
                    'xadmin/vendor/flot/jquery.flot.resize.js','xadmin/vendor/flot/jquery.flot.aggregate.js','xadmin/vendor/flot/jquery.flot.categories.js']
        }
    },
    "image-gallery": {
        "css": {
            'dev': 'xadmin/vendor/bootstrap-image-gallery/css/bootstrap-image-gallery.css',
            'production': 'xadmin/vendor/bootstrap-image-gallery/css/bootstrap-image-gallery.css',
        },
        "js": {
            'dev': ['xadmin/vendor/load-image/load-image.js', 'xadmin/vendor/bootstrap-image-gallery/js/bootstrap-image-gallery.js'],
            'production': ['xadmin/vendor/load-image/load-image.min.js', 'xadmin/vendor/bootstrap-image-gallery/js/bootstrap-image-gallery.js']
        }
    },
    "select": {
        "css": {
            'dev': ['xadmin/vendor/select2/select2.css', 'xadmin/vendor/selectize/selectize.css', 'xadmin/vendor/selectize/selectize.bootstrap3.css'],
        },
        "js": {
            'dev': ['xadmin/vendor/selectize/selectize.js', 'xadmin/vendor/select2/select2.js', 'xadmin/vendor/select2/select2_locale_%(lang)s.js'],
            'production': ['xadmin/vendor/selectize/selectize.min.js', 'xadmin/vendor/select2/select2.min.js', 'xadmin/vendor/select2/select2_locale_%(lang)s.js']
        }
    },
    "multiselect": {
        "css": {
            'dev': 'xadmin/vendor/bootstrap-multiselect/css/bootstrap-multiselect.css',
        },
        "js": {
            'dev': 'xadmin/vendor/bootstrap-multiselect/js/bootstrap-multiselect.js',
        }
    },
    "snapjs": {
        "css": {
            'dev': 'xadmin/vendor/snapjs/snap.css',
        },
        "js": {
            'dev': 'xadmin/vendor/snapjs/snap.js',
        }
    },
}
