class Zones():
    """A class to store and utilize formation tops across the geom."""

    def __init__(self,**kwargs):
        """Initializes the Zone with named top values."""

        keys,tops = [],[]

        for name,vals in kwargs.items():
            keys.append(name)
            tops.append(vals)

        sorted_pairs = sorted(zip(tops,keys))

        if sorted_pairs:
            self._tops,self._keys = zip(*sorted_pairs)
        else:
            self._tops,self._keys = [],[]

    def index(self,key):
        """Returns the index of formation based on its name."""
        return self.keys.index(key)

    def __getitem__(self,key):
        """Returns the list of formation tops based on formation name."""
        return self.tops[self.index(key)]

    def limit(self,key):
        """Returns the list of formation tops and bottoms based on formation name."""
        return self.tops[self.index(key)], self.tops[self.index(key)+1]
 
    @property
    def keys(self):
        """Getter for the formation keys."""
        return self._keys

    @property
    def tops(self):
        """Getter for the formation tops."""
        return self._tops

if __name__ == "__main__":

    zones = Zones()

    print(zones.tops)
    print(zones.keys)