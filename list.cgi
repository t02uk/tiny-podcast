#!/usr/bin/ruby

require 'cgi'
require 'setting.rb'

class MyList

    def initialize
        @cgi = CGI.new
        @dirs = []

        content = dispatch

        @cgi.out do
            content
        end
    end

    def dispatch
        Dir.glob("#{FILE_DIR_BASE}*") do |file|
            file =~ /^\.$/ and next
            file =~ /^\.\.$/ and next
            not File.directory?(file) and next
            @dirs.push(File.basename(file))
        end

        ret = ''
        ret += <<-HERE
        <html>
        <body>
        <ul>
        HERE
        @dirs.each do |dir|
        ret += <<-HERE
        <li><a href="#{BASE_URI}/feed.cgi?item=#{dir}">#{dir}</a></li>
        HERE
        end
        ret += <<-HERE
        </ul>
        </body>
        </html>
        HERE

        return ret
    end

    def debug msg
        @cgi.out do
            msg.gsub(/(\r\n|\r|\n)/, '<br>')
        end
    end
end


my_list = MyList.new()
begin
    my_list.dispatch
    Exception.new
rescue Exception => e
    my_list.debug("!!ERROR: " + e.inspect + "<br>")
    my_list.debug("!!ERROR: " + e.message + "<br>")
    my_list.debug("!!ERROR: " + e.backtrace.inspect + "<br>")
end
