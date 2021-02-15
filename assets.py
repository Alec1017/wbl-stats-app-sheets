from flask_assets import Bundle

bundles = {
    'main_css': Bundle(
        'scss/mixins/*.scss',
        'scss/pages/*.scss',
        'scss/*.scss',
        depends='scss/**/*.scss',
        output='css/main.%(version)s.css'
    )
}