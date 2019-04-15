db.containers.updateMany(
    {container:{$regex:"(AZLU|CASU|CMUU|CPSU|CSQU|CSVU|FANU|HAMU|HLBU|HLCU|HLXU|ITAU|IVLU|LBIU|LNXU|LYKU|MOMU|QIBU|QNNU|TLEU|TMMU|UACU|UAEU|UASU)"}},
    {$set:{carrier:"Hapag-Lloyd"}}
)
// scraper3: 2422 results

db.containers.updateMany(
    {container:{$regex:"(APMU|COZU|FAAU|FRLU|KNLU|LOTU|MAEU|MALU|MCAU|MCHU|MCRU|MHHU|MIEU|MMAU|MNBU|MRKU|MRSU|MSAU|MSFU|MSKU|MSWU|MVIU|MWCU|MWMU|OCLU|POCU|PONU|SCMU|TORU)"}},
    {$set:{carrier:"Maersk"}}
)
// scraper3: 3096 results

db.containers.updateMany(
    {container:{$regex:"(EGHU|EGSU|EISU|EMCU|HMCU|IMTU|LTIU|UGMU)"}},
    {$set:{carrier:"Evergreen"}}
)
// scraper3: 1047 results

db.containers.updateMany(
    {container:{$regex:"(AMFU|AMZU|AXIU|CEOU|CHIU|CLHU|GAEU|GATU|GAZU|HCIU|KWCU|LLTU|MAGU|MAXU|MGLU|MLCU|PRSU|TEMU|TENU|TEXU|TGBU|TGHU|TXGU|WCIU|XINU)"}},
    {$set:{carrier:"Textainer"}}
)
// scraper3: 2850 results
