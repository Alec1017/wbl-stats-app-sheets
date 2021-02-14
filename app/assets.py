from flask_assets import Bundle

bundles = {
    'main_css': Bundle(
        'scss/main.scss',
        depends='scss/**/*.scss',
        output='css/main.%(version)s.css',

    )
}