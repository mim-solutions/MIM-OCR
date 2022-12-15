#
#  Makefile 
#     make all   build the executable
#     make clean erase objects files and executable


# build configuration.
# available configs :
#   - debug
#   - release
CONFIG = debug


# customize this variable to use a specific suffix for g++ (e.g. -4.4)
COMPILER_SUFFIX = 


#
# Compilers
#
CC  = g++$(COMPILER_SUFFIX)


#
# Target specifications
#
#   - name
#   - major version
#   - minor version
#
TARGET          = CppImage2Json16
INTERMEDIATE_DIR = ./$(CONFIG)
INSTALL_DIR      = ../../../bin


#
# Sources directories
#
TARGET_SRC = .
COMMON_SRC = ../Common

IDRSKRN_INCLUDE = ../../../include
IDRSKRN_LIB     = ../../../lib


#
# Compile options
#
DFLAGS = -DPOSIX
IFLAGS = -I$(TARGET_SRC) -I${COMMON_SRC} -I$(IDRSKRN_INCLUDE)
CFLAGS = $(IFLAGS) $(DFLAGS) -fPIC -m64 -std=c++11
LFLAGS = -L$(IDRSKRN_LIB)
ifeq ($(CONFIG), debug)
  DFLAGS += -D_DEBUG
  CFLAGS  += -g
else
  DFLAGS += -D_NDEBUG
  CFLAGS  += -O3
endif

#
# Source files
#
SOURCES = \
  $(TARGET_SRC)/CppImage2Json.cpp \
  $(COMMON_SRC)/CSampleSetup.cpp \



$(INTERMEDIATE_DIR)/%.o : $(TARGET_SRC)/%.cpp
	$(CC) $(CFLAGS) -o $@ -c $<

$(INTERMEDIATE_DIR)/%.o : $(COMMON_SRC)/%.cpp
	$(CC) $(CFLAGS) -o $@ -c $<


#
# Objects list
#
OBJECTS = \
  $(INTERMEDIATE_DIR)/CppImage2Json.o \
  $(INTERMEDIATE_DIR)/CSampleSetup.o \

#
# Targets
#

all:$(TARGET)

$(TARGET) : $(OBJECTS)
	$(CC) -o $(INSTALL_DIR)/$(TARGET) $(OBJECTS) $(LFLAGS) -m64 -lc -lidrskrn16 -ldl -lpthread -lgomp

clean :
	rm -f $(OBJECTS) $(INSTALL_DIR)/$(TARGET)
