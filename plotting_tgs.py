import matplotlib

matplotlib.use("WebAgg")

import matplotlib.pyplot as plt
import mpld3


def get_exon_coordinates(length, junctions):
    exon_coordinates = []
    first = True
    for i, junction in enumerate(junctions):
        if first:
            exon_coordinates.append((0, junction))
            exon_coordinates.append((junction, junctions[i + 1]))
            first = False
        elif i == len(junctions) - 1:
            exon_coordinates.append((junction, length))
        else:
            exon_coordinates.append((junction, junctions[i + 1]))

    return exon_coordinates


def features_defined_by_junctions(exon_coordinates, ORFs):
    features = {}
    for exon in exon_coordinates:
        if exon not in features:
            features[exon] = {"coding": [], "non-coding": []}

        for orf in ORFs:
            if (orf[0] in range(exon[0], exon[1])) and (
                orf[1] in range(exon[0], exon[1])
            ):
                features[exon]["coding"].append((orf[0], orf[1]))
                features[exon]["non-coding"].append((exon[0], orf[0]))
                features[exon]["non-coding"].append((orf[1], exon[1]))

            elif (exon[0] in range(orf[0], orf[1] + 1)) and (
                exon[1] in range(orf[0], orf[1] + 1)
            ):
                features[exon]["coding"].append((exon[0], exon[1]))
                features[exon]["non-coding"].append((exon[0], exon[1]))

            elif orf[0] in range(exon[0], exon[1]):
                features[exon]["non-coding"].append((exon[0], orf[0]))
                features[exon]["coding"].append((orf[0], exon[1]))

            elif orf[1] in range(exon[0] + 1, exon[1]):
                features[exon]["coding"].append((exon[0], orf[1]))
                features[exon]["non-coding"].append((orf[1], exon[1]))

        if (features[exon]["coding"] == []) and (features[exon]["non-coding"] == []):
            features[exon]["non-coding"].append((exon[0], exon[1]))
    return features


def features_despite_junctions(length, ORFs, junctions, noncoding=False):
    features = {"coding": [], "non-coding": []}
    for orf in ORFs:
        closest_upstearm = 0
        closest_downstream = length

        for junction in junctions:
            five_prime_distance = orf[0] - junction
            three_prime_distance = junction - orf[1]

            if (five_prime_distance >= 0) and (
                five_prime_distance < (orf[0] - closest_upstearm)
            ):
                closest_upstearm = junction

            if (three_prime_distance >= 0) and (
                three_prime_distance < (closest_downstream - orf[1])
            ):
                closest_downstream = junction

        features["coding"].append((closest_upstearm, orf, closest_downstream))
        if noncoding:
            features["non-coding"].append(((closest_upstearm, closest_downstream), 1))
    if noncoding:
        for feature1 in features["non-coding"]:
            for feature2 in features["non-coding"]:
                if feature1 != feature2:
                    if (feature1[0][0] >= feature2[0][0]) and (
                        feature1[0][1] <= feature2[0][1]
                    ):
                        features["non-coding"].remove(feature1)

    return features


def orf_frames(ORFs):
    frames = {}

    for orf in ORFs:
        if orf[0] % 3 == 1:
            frames[orf] = "r"
        elif orf[0] % 3 == 2:
            frames[orf] = "b"
        else:
            frames[orf] = "g"

    return frames


def add_non_coding(features, length):

    no_features = [i for i in range(length + 1)]
    for i in range(length + 1):
        for feature in features["coding"]:
            if (i in range(feature[0], feature[2] + 1)) and (i in no_features):
                no_features.remove(i)

    if len(no_features) > 0:
        last = no_features[0]
        consecutive = []
        increasing = False
        for i in no_features:

            if i == last + 1:
                increasing = True
                consecutive.append(last)
                last = i
                if i == no_features[-1]:
                    consecutive.append(i)
                    features["non-coding"].append(
                        ((consecutive[0], consecutive[-1]), 0)
                    )

            elif (i != last + 1) and increasing:
                consecutive.append(last)
                features["non-coding"].append(((consecutive[0], consecutive[-1]), 0))
                consecutive = []
                increasing = False
                last = i

            elif not increasing:
                increasing = False
                last = i
    return features


def numbers_of_features(features, length):

    num_features = []
    for i in range(length):
        features_in_range = 0

        for feature in features["coding"]:
            if i in range(feature[0], feature[2]):
                features_in_range += 1

        for feature in features["non-coding"]:
            if i in range(feature[0][0], feature[0][1]):
                features_in_range += 1

        if features_in_range == 0:
            features_in_range += 1

        num_features.append(features_in_range)

    return num_features


def check_coordinates_valid(used_space, start, stop, height):
    valid = True
    for feature in used_space:
        if (start in range(feature[0], feature[1])) or (
            stop in range(feature[0], feature[1])
        ):
            if height == feature[2]:
                valid = False

        if (feature[0] in range(start, stop)) or (feature[1] in range(start, stop)):
            if height == feature[2]:
                valid = False
    return valid


def find_valid_space(used_space, start, stop, height):
    height = height + 6
    valid = check_coordinates_valid(used_space, start, stop, height)
    if not valid:
        height = height * -1
        valid = check_coordinates_valid(used_space, start, stop, height)

    if not valid:
        start, stop, height = find_valid_space(used_space, start, stop, height)
        valid = check_coordinates_valid(used_space, start, stop, height)

    if valid:
        return start, stop, height


def assign_heights(features, coding_heights):
    used_space = []
    for orf in features["coding"]:
        valid = check_coordinates_valid(used_space, orf[0], orf[2], coding_heights[orf])
        if valid:
            used_space.append((orf[0], orf[2], coding_heights[orf]))
        else:
            start, stop, height = find_valid_space(
                used_space, orf[0], orf[2], coding_heights[orf]
            )
            coding_heights[orf] = height
            used_space.append((start, stop, height))

    return used_space


def plot_transcript_graph(length, junctions, ORFs):

    exon_coordinates = get_exon_coordinates(length, junctions)
    features = features_despite_junctions(length, ORFs, junctions)
    features = add_non_coding(features, length)

    num_features = numbers_of_features(features, length)

    feature_units = 6 * max(num_features)
    frames = orf_frames(ORFs)

    coding_heights = {feature: 0 for feature in features["coding"]}

    used_space = assign_heights(features, coding_heights)
    plt.axes()

    for orf in features["coding"]:
        coding = plt.Rectangle(
            (orf[1][0], coding_heights[orf]),
            orf[1][1] - orf[1][0],
            4,
            fc=frames[orf[1]],
        )
        five_prime = plt.Rectangle(
            (orf[0], coding_heights[orf] + 1), orf[1][0] - orf[0], 2, fc="k"
        )
        three_prime = plt.Rectangle(
            (orf[1][1], coding_heights[orf] + 1), orf[2] - orf[1][1], 2, fc="k"
        )
        plt.gca().add_patch(coding)
        plt.gca().add_patch(five_prime)
        plt.gca().add_patch(three_prime)

    print(coding)

    print(coding_heights)
    print(used_space)

    print(features)
    for region in features["non-coding"]:
        if region[1] == 1:
            non_coding = plt.Rectangle(
                (region[0][0], -3), region[0][1] - region[0][0], 2, fc="k"
            )
        else:
            non_coding = plt.Rectangle(
                (region[0][0] - 1, 1), region[0][1] - region[0][0] + 2, 2, fc="k"
            )

        plt.gca().add_patch(non_coding)
    ############ ADD EXON JUNCTIONS ##################################
    for junction in junctions:
        plt.plot(
            [junction, junction],
            [-feature_units / 2, feature_units / 2],
            "k--",
            label="line 1",
            linewidth=2,
        )

    return plt.figure()
    # plt.axis('scaled')
    #


## This will launch a webagg server from which the plot will be visible
# plot_transcript_graph(100,[23,50, 70], [(10, 20), (25, 75)])
# plt.plot([1, 2, 3, 4])
# plt.ylabel('some numbers')
# plt.show()
