gulp = require 'gulp'

$ = require('gulp-load-plugins')()
appDir = 'werewolf/app'
staticDir = "#{appDir}/static"

gulp.task 'hbs', ->
  gulp.src "#{staticDir}/templates/**/*.hbs"
    .pipe $.handlebars()
    .pipe $.defineModule 'plain'
    .pipe $.declare namespace: 'werewolf.template'
    .pipe $.concat 'templates.js'
    .pipe gulp.dest "#{staticDir}/scripts"

gulp.task 'default', ['hbs']
