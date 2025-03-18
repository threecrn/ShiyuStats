import json

# Set class constants in initialization
# Load the list of characters from their file
with open("../data/characters.json") as char_file:
    CHARACTERS = json.load(char_file)

# # Load the list of elements from the reactions file
# with open('../data/reaction.json') as react_file:
#     ELEMENTS = list(json.load(react_file).keys())


class Composition:
    """An object that stores information about a particular composition. Has:
    player: a string for the player who used this comp.
    phase: a string for the phase this composition was used in.
    room: a string in the form XX-X-X for the room this comp was used in.
    char_presence: a string --> boolean dict for chars in this comp.
    characters: a list of strings for the names of the chars in this comp.
    elements: a string --> int dict for the num of chars for each element.
    resonance: a string --> boolean dict for which resonances are active.

    Additional methods are:
    resonance_string: returns the resonances active as a string.
    on_res_chars: returns the list of characters activating the resonance.
    char_elemeent_list: returns the list of character's elements.
    """

    def __init__(
        self,
        uid,
        comp_chars,
        phase,
        round_num,
        star_num,
        room,
        info_char,
        bangboo,
        comp_chars_cons,
    ):
        """Composition constructor. Takes in:
        A player, as a UID string
        A composition, as a length-four list of character strings
        A phase, as a string
        A room, as a string
        """
        self.player = str(uid)
        self.phase = phase
        self.room = room
        self.round_num = int(round_num)
        self.star_num = int(star_num)
        self.char_structs(comp_chars, info_char, comp_chars_cons)
        self.bangboo = bangboo
        # self.comp_elements()

    def char_structs(self, comp_chars, info_char, comp_chars_cons):
        """Character structure creator.
        Makes a presence dict that maps character names to bools, and
        a list (alphabetically ordered) of the character names.
        """
        self.char_presence = {}
        self.char_cons = {}
        fives = []
        self.dps = []
        self.subdps = []
        self.stun = []
        self.support = []
        self.anomaly = []
        len_element = {
            "Ice": 0,
            "Fire": 0,
            "Ether": 0,
            "Electric": 0,
            "Physical": 0,
        }
        if comp_chars_cons:
            for char_iter in range(len(comp_chars)):
                self.char_cons[comp_chars[char_iter]] = int(comp_chars_cons[char_iter])
        comp_chars.sort()
        for character in comp_chars:
            self.char_presence[character] = True
            if CHARACTERS[character]["availability"] in ["Limited S", "Standard S"]:
                fives.append(character)

            if character in [
                "Miyabi",
                "Zhu Yuan",
                "Ellen",
                "Soldier 11",
                "Evelyn",
                "Soldier 0 - Anby",
            ]:
                self.dps.insert(0, character)
            if character in [
                "Corin",
                "Billy",
                "Nekomata",
                "Anton",
                "Harumasa",
            ]:
                self.dps.append(character)
            elif character in [
                "Piper",
                "Jane",
                "Yanagi",
            ]:
                self.subdps.insert(0, character)
            elif character in [
                "Grace",
                "Burnice",
            ]:
                self.subdps.append(character)
            elif character in [
                "Anby",
                "Lycaon",
                "Koleda",
                "Qingyi",
                "Lighter",
                "Pulchra",
            ]:
                self.stun.insert(0, character)
            elif character in [
                "Soukaku",
                "Nicole",
                "Rina",
                "Lucy",
                "Seth",
                "Astra Yao",
            ]:
                self.support.insert(0, character)
            elif character in [
                "Caesar",
                "Ben",
            ]:
                self.support.append(character)
            if character in [
                "Grace",
                "Piper",
                "Jane",
                "Burnice",
                "Yanagi",
                "Miyabi",
            ]:
                self.anomaly.append(character)

            if CHARACTERS[character]["element"] == "Ice":
                len_element["Ice"] += 1
            if CHARACTERS[character]["element"] == "Fire":
                len_element["Fire"] += 1
            if CHARACTERS[character]["element"] == "Ether":
                len_element["Ether"] += 1
            if CHARACTERS[character]["element"] == "Electric":
                len_element["Electric"] += 1
            if CHARACTERS[character]["element"] == "Physical":
                len_element["Physical"] += 1
        self.fivecount = len(fives)
        self.characters = self.dps + self.subdps + self.stun + self.support

        if not self.dps and not self.subdps and "Soukaku" in self.support:
            self.support.remove("Soukaku")
            self.dps.append("Soukaku")

        """Name structure creator.
        """
        # comp_names = {
        # }
        self.comp_name = "-"
        self.alt_comp_name = "-"
        self.dual_comp_name = "-"
        # for comp_name in comp_names:
        #     if self.characters in comp_names[comp_name]:
        #         self.comp_name = comp_name
        #         break

        if self.comp_name == "-":
            # if len(self.anomaly) >= 1:
            #     if len(self.anomaly) > 2:
            #         self.alt_comp_name = self.characters[0] + " Triple Anomaly"
            #     elif len(self.anomaly) > 1:
            #         self.alt_comp_name = self.characters[0] + " Dual Anomaly"
            #     # elif len(self.dps) + len(self.subdps) == 1:
            #     #     self.alt_comp_name = self.characters[0] + " Solo Anomaly"

            archetype = ""
            # if len(self.support) == 0:
            #     archetype = " No Support"
            #     self.alt_comp_name = self.characters[0] + " No Support"
            if len(self.dps) + len(self.subdps) > 1:
                if len(self.anomaly) >= 1:
                    archetype = " Anomaly"
                elif len(self.dps) + len(self.subdps) > 2:
                    archetype = " Triple Carry"
                else:
                    archetype = " Dual Carry"
                self.dual_comp_name = self.characters[1] + archetype
            else:
                if len(self.support) > 1:
                    archetype = " Dual Support"
                elif len(self.stun) > 0:
                    archetype = " Stun"

            if self.dps or self.subdps or self.stun:
                self.comp_name = self.characters[0] + archetype
            else:
                self.comp_name = "Full Support"

    # def comp_elements(self):
    #     """Composition elements tracker.
    #     Creates a dict that maps elements to number of chars with that element,
    #     and a dict that maps the resonance(s) the comp has to booleans.
    #     """
    #     self.elements = dict.fromkeys(ELEMENTS, 0)
    #     for char in self.characters:
    #         self.elements[CHARACTERS[char]["element"]] += 1

    #     # self.resonance = dict.fromkeys(ELEMENTS, False)

    #     # # Add the unique resonance to the list of element resonances,
    #     # # and set it as the default. Technically there's the edge case for
    #     # # if there's < 4 characters, it should be false I think?
    #     # self.resonance['Unique'] = len(self.characters) == 4
    #     # for ele in ELEMENTS:
    #     #     if self.elements[ele] >= 2:
    #     #         self.resonance[ele] = True
    #     #         self.resonance['Unique'] = False

    # def resonance_string(self):
    #     """Returns the resonance of the composition. Two resos are joined by a ,"""
    #     resos = []
    #     for reso in self.resonance.keys():
    #         if self.resonance[reso]:
    #             resos.append(reso)
    #     return ", ".join(resos)

    # def on_res_chars(self):
    #     """Returns the list of characters who match the composition's resonance."""
    #     chars = []
    #     for char in self.characters:
    #         if self.resonance[CHARACTERS[char]["element"]] or self.resonance["Unique"]:
    #             chars.append(char)
    #     return chars

    # def char_element_list(self):
    #     """Returns the characters' elements as a list"""
    #     return [ CHARACTERS[char]['element'] for char in self.characters ]

    def contains_chars(self, chars):
        """Returns a bool whether this comp contains all the chars in included list."""
        for char in chars:
            if not self.char_presence[char]:
                return False
        return True
