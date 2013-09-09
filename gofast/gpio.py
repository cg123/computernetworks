
import cffi

ffi = cffi.FFI()

ffi.cdef("""
int setup(void);
void setup_gpio(int gpio, int direction, int pud);
int gpio_function(int gpio);
void output_gpio(int gpio, int value);
int input_gpio(int gpio);
void set_rising_event(int gpio, int enable);
void set_falling_event(int gpio, int enable);
void set_high_event(int gpio, int enable);
void set_low_event(int gpio, int enable);
int eventdetected(int gpio);
void cleanup(void);
    """)
C = ffi.verify(sources=['c_gpio.c'])

write = C.output_gpio
read = C.input_gpio
cleanup = C.cleanup
setup = C.setup_gpio

if C.setup():
    raise RuntimeError("Error initializing GPIO")

INPUT = 1
OUTPUT = 0

HIGH = 1
LOW = 0

PUD_OFF  = 0
PUD_DOWN = 1
PUD_UP   = 2