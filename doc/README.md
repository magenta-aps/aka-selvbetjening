Sphinx/autodoc:
For at benytte autodoc har jeg gjort følgende:
  I doc/conf.py skal sys.path sættes, så Sphinx kan se alle de directories
  hvor der ligger moduler. Jeg tilføjede disse 3:
  ../backend/akasite/rest
  ../backend/akasite
  ../backend

I en given rst-fil kan så tilføje disse direktiver, for at få Sphinx til at
tilføje modul-kode til docs:

.. automodule:: <modulnavn>  
   :members:
Mere info her:
http://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html

Jeg har selv til en start brugt denne syntax til klasser og metoder,
som Sphinx kan opfatte og formattere pænt.


