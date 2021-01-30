

#apt-get install -y libjpeg-progs

SRC="1L"
DST="1L_rotate"
rm -r $DST
mkdir $DST

find $SRC/*.JPG -maxdepth 1 -type f | parallel --progress convert {} -rotate -1 $DST/{/.}.JPG


SRC="1L_rotate"
DST="3L"
rm -r $DST
mkdir $DST

find $SRC/*.JPG -maxdepth 1 -type f | parallel --progress jpegtran \
 -crop 2200x2600+330+400 -outfile $DST/{/.}.JPG  {}

cnt=4
for i in $DST/*.JPG ; do
	let "cnt=cnt+1"
	let "cnt=cnt+1"
	cntstr=$(printf "%04d" $cnt)
    mv -v $i $DST/${cntstr}.JPG
done
 

SRC="2R"
DST="4R"
rm -r $DST
mkdir $DST

find $SRC/*.JPG -maxdepth 1 -type f | parallel --progress jpegtran \
 -crop 2200x2600+172+882 -outfile $DST/{/.}.JPG  {}
 
cnt=7
for i in $DST/*.JPG ; do
	let "cnt=cnt+1"
	let "cnt=cnt+1"
	cntstr=$(printf "%04d" $cnt)
    mv -v $i $DST/${cntstr}.JPG
done

DST="5"
rm -r $DST
mkdir $DST
SRC="4R"
mv -v $SRC/* $DST/
SRC="3L"
mv -v $SRC/* $DST/
