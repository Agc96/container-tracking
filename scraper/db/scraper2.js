db.container_movements.updateMany(
    {container:{$regex:"(AZLU|CASU|CMUU|CPSU|CSQU|CSVU|FANU|FSCU|HAMU|HLBU|HLCU|HLXU|ITAU|IVLU|LBIU|LNXU|LYKU|MOMU|QIBU|QNNU|TLEU|TMMU|UACU|UAEU|UASU)"}},
    {$set:{carrier:"Hapag-Lloyd"}}
)
// scraper2: 7789 results

db.container_movements.updateMany(
    {container:{$regex:"(APMU|COZU|FAAU|FRLU|KNLU|LOTU|MAEU|MALU|MCAU|MCHU|MCRU|MHHU|MIEU|MMAU|MNBU|MRKU|MRSU|MSAU|MSFU|MSKU|MSWU|MVIU|MWCU|MWMU|OCLU|POCU|PONU|SCMU|TORU)"}},
    {$set:{carrier:"Maersk"}}
)
// scraper2: 172 results

db.container_movements.updateMany(
    {container:{$regex:"(EGHU|EGSU|EISU|EMCU|HMCU|IMTU|LTIU|UGMU)"}},
    {$set:{carrier:"Evergreen"}}
)
// scraper3: 990 results
