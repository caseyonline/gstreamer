CC=g++
CFLAGS=`pkg-config --cflags --libs gstreamer-1.0`
OBJ = src/test1.o \
			src/test2.o \
			src/test3.o \
			src/gstreamer.o

SYS=_$(shell uname -s)

gstreamer: $(OBJ)
	$(CC) -o $@ $^ $(CFLAGS) $(LIBS)

%.o: %.cxx
	$(CC) -c -o $@ $< $(CFLAGS)
