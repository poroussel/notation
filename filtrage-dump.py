# -*- coding: utf-8 -*-

import sys
from django.utils import simplejson

if __name__ == "__main__":
    if len(sys.argv) == 2:
        inf = file(sys.argv[1])
        data = simplejson.load(inf)

        data = [el for el in data if el['model'] != 'notation.note']
        data = [el for el in data if el['model'] != 'notation.capacite']
        data = [el for el in data if el['model'] != 'notation.ensemblecapacite']
        print simplejson.dumps(data, indent=2)
                
        inf.close()
        
