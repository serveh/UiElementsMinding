import spacy
import nltk
from nltk.stem.snowball import SnowballStemmer
from imageListParser import ImageListParser
from nltk.stem.porter import PorterStemmer
import os

nlp = spacy.load('en')


def lemmatizing(doc):
    porter_stemmer = PorterStemmer()
    is_noun = lambda pos: pos[:2] == 'NN' or pos[:2] == 'VB'
    word_data = doc
    nltk_tokens = nltk.word_tokenize(word_data)
    nouns = [porter_stemmer.stem(word) for (word, pos) in nltk.pos_tag(nltk_tokens) if is_noun(pos)]
    return nouns


prefix_to_remove = ['A close up of a',
                    'A drawing of a']
concat_elem = lambda x, y: x + ',' + y
flatten_list = lambda x, y: x + y


def remove_common_prefix(in_str, prefix_to_move):
    for pp in prefix_to_remove:
        in_str = in_str.replace(pp, '')

    return in_str


def process_a_file(filename):
    ilp = ImageListParser()
    is_loaded = ilp.load(filename)
    assert is_loaded

    output_fname = filename.replace('imageListAzure.txt', 'lemmetizied_image_text.txt')
    fp = open(output_fname, 'w')
    for img in ilp.image_list:
        cap = ilp.image_caption[img]
        tags = ilp.image_tags[img]
        img_parts = img.replace('_', ' ')[:len(img) - 4]
        cap = remove_common_prefix(cap, prefix_to_remove)
        img_name_l = lemmatizing(img_parts) or ['noname']
        cap_l = lemmatizing(cap) or ['nocapt']
        tags_l = reduce(flatten_list, map(lemmatizing, filter(None, tags.split(',')))) or ['notag']
        fp.write('{}; {}; {}; {}\n'.format(img,
                                           reduce(concat_elem, cap_l),
                                           reduce(concat_elem, tags_l),
                                           reduce(concat_elem, img_name_l)))


AZURE_FILE = 'imageListAzure.txt'

def main():
    app_root_folder = '/home/srwe/work/project/backstage/apks'
    all_folders = os.listdir(app_root_folder)
    for cur_folder in all_folders:
        cur_folder_fp = os.path.join(app_root_folder, cur_folder)
        if os.path.isdir(cur_folder_fp):
            azure_output_file = os.path.join(cur_folder_fp, AZURE_FILE)
            if os.path.exists(azure_output_file):
                try:
                    process_a_file(azure_output_file)
                except:
                    print('Error processing {}'.format(azure_output_file))
                    raise
            else:
                print('The Azure output file does not exist for this app {} '.format(cur_folder_fp))


if __name__ == "__main__":
    process_a_file('/home/srwe/work/project/backstage/apks/air.com.demute.TaoMix_v1.1.13/imageListAzure.txt')
    #main()


'''

############
doc = nlp(doc.decode('utf-8', 'ignore'))
    for token in doc:
        stemmer = SnowballStemmer("english")
        print (stemmer.stem(token.lemma_).encode('ascii').decode('unicode-escape'))
    
'''