from more_itertools import locate
import random


def balance_data(main_field, *args):
    for arg in args:
        if len(arg) != len(main_field):
            print('of main files:'.format())
    unique_elements = list(set(main_field))
    class_indices = []
    num_min_element = len(main_field)
    for elem in unique_elements:
        pred = lambda x : x == elem
        item_idx = list(locate(main_field, pred))
        class_indices.append(item_idx)
        print('number of instances in class {}: {}'.format(elem, len(item_idx)))
        num_min_element = min(num_min_element, len(item_idx))

    balanced_dataset = [None] * (len(args) + 1)
    # now balance data
    for idx, elem in enumerate(unique_elements):
        samples = random.sample(class_indices[idx], num_min_element)
        tmp = [main_field[e] for e in samples]

        #print(class_indices[idx], ' -> ', samples)
        #print(tmp, ' === ')
        if balanced_dataset[0]:
            balanced_dataset[0].extend(tmp)
        else:
            balanced_dataset[0] = tmp

        for ii, arg in enumerate(args):
            tmp = [arg[e] for e in samples]
            # print(tmp)
            if balanced_dataset[ii + 1]:
                balanced_dataset[ii + 1].extend(tmp)
            else:
                balanced_dataset[ii + 1] = tmp

    return balanced_dataset  # , class_indices


if __name__ == '__main__':
    l1 = [1,1,1,1,1,1,1,2,2,2,2,1,1,1,2,2,2,1]
    l2 = [4,4,4,4,4,4,4,6,6,6,6,4,4,4,6,6,6,4]
    l1_out, l2_out = balance_data(l1, l2)

    print l1_out, ' ====== ', l2_out
    print('Done!!')
