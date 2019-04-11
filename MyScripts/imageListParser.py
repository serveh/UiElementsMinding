import os

class ImageListParser:

    def __init__(self):
        self.filename = None
        self.image_list = []
        self.image_caption = dict()
        self.image_tags = dict()
        self.image_name = dict()

    #def __getitem__(self, key):
        #return self.book[key]

    def load(self, filename):
        if os.path.isfile(filename):
            self._load_parse(filename)
            b_res = True
        else:
            print('Error opening {}'.format(filename))
            b_res = False
        return b_res

    def _load_parse(self, filename):
        fp = open(filename, 'r')
        self.image_list = []
        self.image_caption = dict()
        self.image_tags = dict()
        self.image_name = dict()
        for li in fp:
            parts = li.rstrip().split(';')
            if len(parts) == 4:
                self.image_list.append(parts[0])
                self.image_caption[parts[0]] = parts[1]
                self.image_tags[parts[0]] = parts[2]
                self.image_name[parts[0]] = parts[3]
            elif len(li.rstrip()) == 0:
                print('Got an empty line')
            else:
                print('Error un expected line: {} {}'.format(li, filename))
                quit()
        fp.close()
        self.filename = filename

    def get_caption_tag_name(self, image_file):
        cap = None
        tag = None
        name = None
        if image_file in self.image_list:
            cap, tag, name = self.image_caption[image_file], self.image_tags[image_file], self.image_name[image_file]
        return cap, tag, name


if __name__ == '__main__':
    ilp = ImageListParser()
    is_loaded = ilp.load('/home/srwe/work/project/backstage/apks/air.com.demute.TaoMix_v1.1.13/lemmetizied_image_text.txt')
    cap, tags, name = ilp.get_caption_tag_name('mp_warning_32x32_n.png')
    print(cap, tags, name)
    print(is_loaded)