try:
    from PIL import Image
    from glob import glob
    from sys import argv
except ModuleNotFoundError:
    import pip

    pip.main(['install', '--quiet', 'Pillow'])
    from PIL import Image
    from glob import glob
    from sys import argv


class ImageConverter:
    def convert_image(self, path):
        img = Image.open(path)
        size = img.size
        bytes = []
        for i in range(size[0] // 16):
            for j in range(size[1]):
                row = ''
                for k in range(16):
                    row += str(img.getpixel((16 * i + k, j)))
                bytes.append(self.__normalize_bytes(int(row[::-1], 2)))
        return size[0] // 16, size[1] // 16, bytes

    def convert_to_jack(self, bytes):
        code = []
        for i in range(len(bytes)):
            code.append(f'\t\tlet content[{i}] = {bytes[i]};')
        return '\n'.join(code)

    def convert_image_to_jack(self, path):
        image_info = self.convert_image(path)
        return image_info[0], image_info[1], self.convert_to_jack(image_info[2])

    def convert_directory(self, path):
        image_names = sorted(glob(f'{path}/*.png'))
        return [self.convert_image_to_jack(f'{name}') for name in image_names]

    def convert_to_sprite_loader(self, jack_images):
        begin = '''class SpriteLoader
{
    field Array Sprites;

    constructor SpriteLoader new()
    {
        var Sprite sprite;
        var Array content;
        let Sprites = ''' + f'Array.new({len(jack_images)});\n\n'
        sprites = []
        for i in range(len(jack_images)):
            sprite = f'\t\tlet content = Array.new({jack_images[i][0] * jack_images[i][1] * 16});\n{jack_images[i][2]}\n\t\tlet sprite = Sprite.new(Vector.new(0, 0), Vector.new({jack_images[i][0]}, {jack_images[i][1]}), content);\n\t\tlet Sprites[{i}] = sprite;\n'
            sprites.append(sprite)
        end = '''
        return this;
    }

    method void dispose()
    {
        do Sprites.dispose();
        do Memory.deAlloc(this);
        return;
    }

    method Array getSprites()
    {
        return Sprites;
    }
}'''
        return begin + ''.join(sprites) + end


    def __normalize_bytes(self, byte):
        if byte > 2 ** 15 - 1:
            return byte - 2 ** 16
        return byte


if __name__ == '__main__':
    converter = ImageConverter()
    result = converter.convert_to_sprite_loader(converter.convert_directory(argv[1]))
    with open(f'{argv[1]}SpriteLoader.jack', 'w') as file:
        file.write(result)
