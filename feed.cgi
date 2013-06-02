#!/usr/bin/ruby

require 'cgi'
require 'erb'
require 'time'
require 'setting.rb'
require 'uri'


class MyFeed

    TEMPLATE_FILENAME='feed.rhtml'

    class TitleConverter
        TITLE_FILE_NAME = "title.rb"
        def initialize basedir
            filename = "#{basedir}/#{TITLE_FILE_NAME}"
            if File.exists?(filename) then
                @cache = eval(File.read(filename))
            end
        end

        def convert id
            if @cache
                @cache[id] || id
            else
                id
            end
        end
    end

    def initialize
        @cgi = CGI.new
        @rdf = {}

        @params = {}
        @cgi.params.each_pair do |key, value|
            @params[key] = URI.unescape(value[0])
        end
    end

    def refresh_thumb(dir, filebase)
        unless File.exist?("#{dir}/thumb/#{filebase}.jpg")
            system("ffmpeg -i \"#{dir}/#{filebase}.mp4\" -f mjpeg -ss 5 -s 240x180 -vframes 1 -an \"#{dir}/thumb/#{filebase}.jpg\"")
        end
    end

    def video_type?(item)
        item['type'] =~ /video/
    end

    def dispatch
        analyze @params['item']

        @options = {
            "type" => "application/xml",
            "charset" => "utf-8",
            #'Content-Disposition' => "attachment; filename=\"feed.xml\""
        }

        @cgi.out @options do
            to_feed
        end
    end

    def analyze item_name
        @rdf['items'] = analyze_item(item_name)
        @rdf['header'] = analyze_header(item_name)
    end

    def analyze_header item_name
        header = {}
        header['item_name'] = item_name
        header['last_date'] = @rdf['items'].first['date']
        return header
    end

    def analyze_item item_name
        items = []
        basedir = "#{FILE_DIR_BASE}/#{item_name}"
        tc = TitleConverter::new(basedir)
        Dir.glob("#{basedir}/*") do |file|
            base = File.basename(file)
            base =~ /^\.$/ and next
            base =~ /^\.\.$/ and next
            mimetype = get_mimetype(base) or next

            item = {}
            item['type'] = mimetype
            item['name_base'] = base.sub(/(.+)\..+/){$1}
            item['title'] = tc.convert(item['name_base'])
            item['name_ext'] = base.sub(/.+\.(.+)/){$1}
            item['name_full'] = URI.escape(base)
            item['date'] = File.mtime(file)
            item['size'] = File.size(file)

            items.push item

            if video_type?(item)
                #refresh_thumb("#{FILE_DIR_BASE}/#{item_name}", "#{item['name_base']}")
            end
        end

        items = items.sort_by{|item|
            item['date']
        }.reverse
        return items
    end


    def get_mimetype file_name
        patterns = {
            /\.mp3$/ => 'audio/mpeg',
            /\.m4a$/ => 'audio/x-m4a',
            /\.mp4$/ => 'video/mp4',
            /\.m4v$/ => 'video/x-m4v',
            /\.mov$/ => 'video/quicktime',
            /\.aac$/ => 'audio/aac',
            /\.pdf$/ => 'application/pdf'
        }
        matched = patterns.find {|item|
            file_name =~ item[0]
        }

        return matched ? matched[1] : nil
    end

    def to_feed
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


my_feed = MyFeed.new()
begin
    my_feed.dispatch
    Exception.new
rescue Exception => e
    my_feed.debug("!!ERROR: " + e.inspect + "<br>")
    my_feed.debug("!!ERROR: " + e.message + "<br>")
    my_feed.debug("!!ERROR: " + e.backtrace.inspect + "<br>")
end
