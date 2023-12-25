#!/usr/bin/env bash
# docker_build tesseract

dnf install -y gcc gcc-c++ make
dnf install -y autoconf aclocal automake
dnf install -y libtool
dnf install -y libjpeg-devel libpng-devel libpng-devel libtiff-devel zlib-devel

cd ~
dnf install -y tar git wget


cd ~
dnf install clang -y
dnf install libpng-devel libtiff-devel zlib-devel libwebp-devel libjpeg-turbo-devel -y
wget https://github.com/DanBloomberg/leptonica/releases/download/1.75.1/leptonica-1.75.1.tar.gz
tar -xzvf leptonica-1.75.1.tar.gz
cd leptonica-1.75.1
./configure && make &&  make install


#install autoconf-archive
cd ~
wget https://gnu.mirror.constant.com/autoconf-archive/autoconf-archive-2010.06.04.tar.gz
tar -xvf autoconf-archive-2010.06.04.tar.gz
cd autoconf-archive-2010.06.04
./configure && make && make install
cp m4/* /usr/share/aclocal/


# tesseract
cd ~
sudo yum install git-core libtool pkgconfig -y
git clone --depth 1  https://github.com/tesseract-ocr/tesseract.git tesseract-ocr
cd tesseract-ocr
export PKG_CONFIG_PATH=/usr/local/lib/pkgconfig
./autogen.sh
./configure
make
make install

#tessdata
cd /root/tesseract-ocr/tessdata
#traindata for tesseract
wget https://github.dev/tesseract-ocr/tessdata/blob/main/eng.traineddata
