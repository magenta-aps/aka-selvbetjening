==========
Inkasso 
==========

REST-api til indberetning af inkasso. 


Generelle Felter
================

Navnene er felt-navn i filupload til Masseoprettelse, fra *Vejledning_om_brug_af_web_fordringshaver.pdf*
(Paranteser viser hvilket felt det ser ud til at passe til i formularen)

- Fordringshaver
    - Samme som man er logget ind som

- Debitor
    - Cpr eller GER(CVR) nr. Så 8 eller 10 cifre
    - Evt lav modulo11 check på cpr
    
- Anden fordringshaver
    - Skal vel nok valideres til rent faktisk at være en fordringshaver

- (MANGLER INFO) Fordringsgruppenr. (Ekstern fordringsgruppe) 
    - Der findes et antal af præ-definerede grupper, men vi kender ikke til dem.
    - Der skulle vist være nogle regler for hvilke andre felter der skal bruges ud fra dette felt.

- (MANGLER INFO) Fordringstypenr. (Ekstern fordringstype)
    - Der findes et antal af præ-definerede typer, men vi kender ikke til dem.
    - Der skulle vist være nogle regler for hvilke andre felter der skal bruges ud fra dette felt.

- Barn cpr 
    - Skulle vist kun være relevant ved nogle fordrings-grupper/typer
    - Evt lav modulo11 check

- Ekstern posteringsnr. (Eksternt sagsnummer?)
    - Det ligner at dette felt i filupload, svarer til feltet *Eksternt sagsnummer*, er det det?

- Hovedstol/Rest restance (Hovedstol)
    - Dette er et beløb, alle beløb afrundes til max 2 cifre.

- Posteringstekst 
    - til Hovedstol

- Bankrente
    - Dette er et beløb, alle beløb afrundes til max 2 cifre.

- Posteringstekst 
    - til Bankrente

- Bankgebyr
    - Dette er et beløb, alle beløb afrundes til max 2 cifre.

- Posteringstekst
    - til Bankgebyr

- Rente
    - Dette er et beløb, alle beløb afrundes til max 2 cifre.

- Posteringstekst
    - til Rente

- (MANGLER INFO)Kontaktperson
    - Er dette bare noget tekst, eller et cpr nummer, eller hvad?

- Periodestart
    - Dato, i eksemplet skrives det som "DD-MM-ÅÅÅÅ"

- Periodeslut
    - Dato, i eksemplet skrives det som "DD-MM-ÅÅÅÅ"

- Forfaldsdato
    - Dato, i eksemplet skrives det som "DD-MM-ÅÅÅÅ"

- Betalingsdato
    - Dato, i eksemplet skrives det som "DD-MM-ÅÅÅÅ"

- Forældelsesdato
    - Dato, i eksemplet skrives det som "DD-MM-ÅÅÅÅ"

- Notat

- Meddebitorer - komma-sepereret liste ad meddebitorer 



Opret Sag
=========


Masseopret Sager
================


Vis Sager
=========


Eksporter Inkassosager
======================

