require 'open3'

module Jekyll
  module ImageDimensions
    # Reserve the original aspect ratio before responsive images finish loading.
    def image_dimensions(path)
      site = @context.registers[:site]
      source = File.expand_path(site.source)
      image = File.expand_path(path.to_s.sub(%r{\A/}, ''), source)
      return {} unless image.start_with?(source + File::SEPARATOR) && File.file?(image)

      @image_dimensions_cache ||= {}
      @image_dimensions_cache[image] ||= begin
        output, status = Open3.capture2(
          'identify', '-ping', '-format', '%w %h %[orientation]', "#{image}[0]", err: File::NULL
        )
        width, height, orientation = output.split
        width, height = width.to_i, height.to_i
        width, height = height, width if %w[LeftTop RightTop RightBottom LeftBottom].include?(orientation)
        status.success? && width.positive? && height.positive? ? { 'width' => width, 'height' => height } : {}
      rescue Errno::ENOENT
        {}
      end
    end
  end
end

Liquid::Template.register_filter(Jekyll::ImageDimensions)
