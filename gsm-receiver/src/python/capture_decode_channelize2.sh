#!/bin/bash

#
# Add only the CA (Cell Allocation) according to SI type 1
#
CONFIGURATION="7T"
#CA="18 21 30 32 42 61"
CA="12 22 33 42 49 54"
C0="33"
MA="07"
MAIO=2
HSN=2
KEY="00 00 00 00 00 00 00 00"
KEY="88 0b 84 cd 8f 24 74 00"
NSAMPLES=256000000

#############################################################

for x in $CA
do
  CA_FILES="$CA_FILES out/out_$x.cf"
done

minARFCN=`echo $CA | awk '{print $1}'`
maxARFCN=`echo $CA | awk '{print $NF}'`
c0POS=`echo $CA | awk -vchan=$C0 '{for(i=1;i<=NF;i++) if($i==chan)print (i-1)}'`
if [ x$c0POS == x ]
then
  echo "The main channel cannot be found in CA"
  exit
fi

ARFCN_fc=$((($maxARFCN+$minARFCN)/2))

if [ $ARFCN_fc -gt 125 ]
then
  FC=$((1805200000 + 200000*$(($ARFCN_fc-512))))
else
  FC=$((935000000 + 200000*$ARFCN_fc))
fi

BW=$((($maxARFCN-$minARFCN+1)*200))

if [ $BW -gt 10000 ]
then
  SR=25000000
  NCHANNELS=125
  pfbDECIM=46
  totDECIM=184
elif [ $BW -gt 200 ]
then
  SR=10000000
  NCHANNELS=50
  pfbDECIM=17
  totDECIM=170
elif [ $BW -eq 200 ]
then
  SR=574712
  NCHANNELS=1
  pfbDECIM=1
  totDECIM=174
fi

echo "min_ARFCN: $minARFCN"
echo "max_ARFCN: $maxARFCN"
echo "Center ARFCN: "$ARFCN_fc
echo "Center frequency: $FC"khz
echo "Sampling rate: $SR" 
echo "Number of samples: $NSAMPLES"
echo "CA files: $CA_FILES"
echo "C0 ARFCN: $C0"
echo "C0 position: $c0POS"

if [ $CONFIGURATION == "0B" ]
then
  #sudo uhd_rx_cfile.py -g 76 -f "$FC" --samp-rate="$SR" out/out.cf -N "$NSAMPLES"
  ./channelize2.py --inputfile="out/out.cf" --arfcn="$ARFCN_fc" --srate="$SR" --decimation="$pfbDECIM" --nchannels="$NCHANNELS" --nsamples=$NSAMPLES
  ./gsm_receive100_channelize.py -d "$totDECIM" -c "$CONFIGURATION" -k "$KEY" --c0pos $c0POS --ma "$MA" --maio $MAIO --hsn $HSN --inputfiles "$CA_FILES"
else
  ./gsm_receive100_channelize.py -d "$totDECIM" -c "$CONFIGURATION" -k "$KEY" --c0pos $c0POS --ma "$MA" --maio $MAIO --hsn $HSN --inputfiles "$CA_FILES"
fi

