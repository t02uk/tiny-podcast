#!/usr/bin/ruby

require 'cgi'
require 'erb'
require 'time'
require 'setting.rb'
require 'uri'


class MyOpml

    TEMPLATE_FILENAME='opml.rhtml'

    def initialize
        @cgi = CGI.new
        @rdf = {}

        @params = {}
        @cgi.params.each_pair do |key, value|
            @params[key] = URI.unescape(value[0])
        end
    end

    def dispatch

        analyze

        @options = {
            "type" => "application/xml",
            "charset" => "utf-8",
            #'Content-Disposition' => "attachment; filename=\"opml.xml\""
        }

        @cgi.out @options do
            to_opml
        end
    end

    def analyze
        @rdf['items'] = analyze_item
        @rdf['header'] = analyze_header
    end

    def analyze_header
        header = {}
        header['date_created'] = Time.now
        return header
    end

    def analyze_item

        items = []
        Dir.glob("#{FILE_DIR_BASE}/*") do |file|
            item = {}
            file =~ /^\.$/ and next
            file =~ /^\.\.$/ and next
            not File.directory?(file) and next
            dir = File.basename(file)
            item['url'] = "#{BASE_URI}/feed.cgi?item=#{CGI.escape(dir)}"
            item['title'] = dir
            items.push(item)
        end

        return items
    end

    def to_opml
        open("podcast/#{TEMPLATE_FILENAME}") do |data|
            eval(ERB.new(data.read, nil, '-').src, binding, __FILE__, __LINE__)
        end
    end

    def debug msg
        @cgi.out do
            msg.gsub(/(\r\n|\r|\n)/, '<br>')
        end
    end
end


my_opml = MyOpml.new()
begin
    my_opml.dispatch
    Exception.new
rescue Exception => e
    my_opml.debug("!!ERROR: " + e.inspect + "<br>")
    my_opml.debug("!!ERROR: " + e.message + "<br>")
    my_opml.debug("!!ERROR: " + e.backtrace.inspect + "<br>")
end
