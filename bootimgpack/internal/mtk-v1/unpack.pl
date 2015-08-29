#!/usr/bin/perl

#
#
# Change history:
#   - add support mt6752/mt6732/mt6595 by cofface 20150127
#

use v5.14;
use warnings;
use bytes;
use File::Path;
use File::Basename;
use Compress::Zlib;
use Term::ANSIColor;
use Scalar::Util qw(looks_like_number);
use FindBin qw($Bin);
use Text::Wrap;

my $version = "mtk-unpack script by cofface 20150812\n";
my $usageMain = "unpack-MTK.pl <infile> [COMMAND ...]\n  Unpacks MTK boot, recovery\n\n";
my $usage = $usageMain;

print colored ("$version", 'bold blue') . "\n";
die "Usage: $usage" unless $ARGV[0];

if ($ARGV[1]) {
	if ($ARGV[1] eq "-info_only" || $ARGV[1] eq "--debug") {
		die "Usage: $usage" unless !$ARGV[2];
	} elsif ($ARGV[1] eq "-kernel_only" || $ARGV[1] eq "-ramdisk_only") {
		die "Usage: $usage" unless (!$ARGV[2] || $ARGV[2] eq "--debug" && !$ARGV[3]);
	} else {
		die "Usage: $usage";
	}
}

my $inputfile = $ARGV[0];
my $inputFilename = fileparse($inputfile);

open (INPUTFILE, "$inputfile")
	or die_msg("couldn't open the specified file '$inputfile'!");
my $input;
while (<INPUTFILE>) {
	$input .= $_;
}
close (INPUTFILE);

sub clean_files {
#clean boot-new.img kernel args.txt ramdisk
if( -e "boot-new.img")
{
unlink("boot-new.img");
}
if( -e "kernel")
{
unlink("kernel");
}
if( -e "args.txt")
{
unlink("args.txt");
}
if( -d "ramdisk")
{
system ("rm -rf ramdisk");
}
}

clean_files();

if (substr($input, 0, 8) eq "ANDROID!") {
	# else, if a valid Android signature is found, try to unpack boot or recovery image
	print "Valid Android signature found...\n";
	if ($ARGV[1]) {
		die_msg("argument '$ARGV[1]' can't be used with boot or recovery images!")
			unless ($ARGV[1] eq "-info_only" || $ARGV[1] eq "-kernel_only" || $ARGV[1] eq "-ramdisk_only" ||
				$ARGV[1] eq "--debug");
		if ($ARGV[1] eq "--debug") {
			unpack_boot($input, "kernel and ramdisk", $ARGV[1]);
		} else {
			$ARGV[1] =~ s/-//;
			$ARGV[1] =~ s/_only//;
			unpack_boot($input, $ARGV[1], $ARGV[2] ? $ARGV[2] : "--normal");
		}
	} else {
		unpack_boot($input, "kernel and ramdisk", "--normal");
	}
} else {
	die_msg("the input file does not appear to be supported or valid!");
}


sub unpack_boot {
	my ($bootimg, $extract, $mode) = @_;
	my ($bootMagic, $kernelSize, $kernelLoadAddr, $ram1Size, $ram1LoadAddr, $ram2Size, $ram2LoadAddr, $tagsAddr, $pageSize, $unused1, $unused2, $bootName, $cmdLine, $id) = unpack('a8 L L L L L L L L L L a16 a512 a20', $bootimg);
	my $magicAddr = 0x00000000;
	my $baseAddr = $kernelLoadAddr - 0x00008000;
	my $kernelOffset = $kernelLoadAddr - $baseAddr;
	my $ram1Offset = $ram1LoadAddr - $baseAddr;
	my $ram2Offset = $ram2LoadAddr - $baseAddr;
	my $tagsOffset = $tagsAddr - $baseAddr;
	my $debug_mode = ($mode =~ /debug/ ? 1 : 0);
	my $unpack_sucess = 0;

	# remove trailing zeros from board and cmdline
	$bootName =~ s/\x00+$//;
	$cmdLine =~ s/\x00+$//;
	
	

	# print input file information (only in normal mode)
	if (!$debug_mode) {
		print colored ("\nInput file information:\n", 'cyan') . "\n";
		print colored (" Header:\n", 'cyan') . "\n";
		printf ("  Boot magic:\t\t\t%s\n", $bootMagic);
		printf ("  Kernel size (bytes):\t\t%d\t\t(0x%.8x)\n", $kernelSize, $kernelSize);
		printf ("  Kernel load address:\t\t0x%.8x\n\n", $kernelLoadAddr);
		printf ("  Ramdisk size (bytes):\t\t%d\t\t(0x%.8x)\n", $ram1Size, $ram1Size);
		printf ("  Ramdisk load address:\t\t0x%.8x\n", $ram1LoadAddr);
		printf ("  Second stage size (bytes):\t%d\t\t(0x%.8x)\n", $ram2Size, $ram2Size);
		printf ("  Second stage load address:\t0x%.8x\n\n", $ram2LoadAddr);
		printf ("  Tags address:\t\t\t0x%.8x\n", $tagsAddr);
		printf ("  Page size (bytes):\t\t%d\t\t(0x%.8x)\n", $pageSize, $pageSize);
		printf ("  ASCIIZ product name:\t\t'%s'\n", $bootName);
		printf ("  Command line:\t\t\t'%s'\n", $cmdLine);
		printf ("  ID:\t\t\t\t%s\n\n", unpack('H*', $id));
		print colored (" Other:\n", 'cyan') . "\n";
		printf ("  Boot magic offset:\t\t0x%.8x\n", $magicAddr);
		printf ("  Base address:\t\t\t0x%.8x\n\n", $baseAddr);
		printf ("  Kernel offset:\t\t0x%.8x\n", $kernelOffset);
		printf ("  Ramdisk offset:\t\t0x%.8x\n", $ram1Offset);
		printf ("  Second stage offset:\t\t0x%.8x\n", $ram2Offset);
		printf ("  Tags offset:\t\t\t0x%.8x\n", $tagsOffset);
	}

	if ($extract eq "info") {
		die colored ("Successfully displayed input file information.", 'green') . "\n";
	}

	# create file containing extra arguments for further repacking
	open (ARGSFILE, ">args.txt")
		or die_msg("couldn't create file 'args.txt'!");
	printf ARGSFILE ("--base %#.8x\n--pagesize %d\n--kernel_offset %#.8x\n--ramdisk_offset %#.8x\n--second_offset %#.8x\n--tags_offset %#.8x%s%s", $baseAddr, $pageSize, $kernelOffset, $ram1Offset, $ram2Offset, $tagsOffset, $bootName eq "" ? "" : "\n--board $bootName", $cmdLine eq "" ? "" : "\n--cmdline $cmdLine") or die;
	close (ARGSFILE);
	print "\nExtra arguments written to 'args.txt'\n";

	if ($extract =~ /kernel/) {
		my $kernel = substr($bootimg, $pageSize, $kernelSize);

		open (KERNELFILE, ">kernel")
			or die_msg("couldn't create file 'kernel'!");
		binmode (KERNELFILE);
		print KERNELFILE $kernel or die;
		close (KERNELFILE);

		print "Kernel written to 'kernel'\n";
		$unpack_sucess = 1;
	}

	if ($extract =~ /ramdisk/) {
		my $kernelAddr = $pageSize;
		my $kernelSizeInPages = int(($kernelSize + $pageSize - 1) / $pageSize);

		my $ram1Addr = (1 + $kernelSizeInPages) * $pageSize;
		my $ram1 = substr($bootimg, $ram1Addr, $ram1Size);

		# chop ramdisk header
		$ram1 = substr($ram1, 512);

		if (substr($ram1, 0, 2) ne "\x1F\x8B") {
			die_msg("the specified boot image does not appear to contain a valid gzip file!");
		}

		open (RAMDISKFILE, ">ramdisk.cpio.gz")
			or die_msg("couldn't create file 'ramdisk.cpio.gz'!");
		binmode (RAMDISKFILE);
		print RAMDISKFILE $ram1 or die;
		close (RAMDISKFILE);

		if (-e "ramdisk") {
			rmtree "ramdisk";
			print "Removed old ramdisk directory 'ramdisk'\n";
		}

		mkdir "ramdisk" or die;
		chdir "ramdisk" or die;
		foreach my $tool ("gzip", "cpio") {
			die_msg("'$tool' binary not found! Double check your environment setup.")
				if system ("command -v $tool >/dev/null 2>&1");
		}
		if ($debug_mode) {
			print colored ("\nRamdisk unpack command:", 'yellow') . "\n";
			print "'gzip -d -c ../ramdisk.cpio.gz | cpio -i'\n\n";
		}
		print "Ramdisk size: ";
		system ("gzip -d -c ../ramdisk.cpio.gz | cpio -i");
		system ("rm ../ramdisk.cpio.gz") unless ($debug_mode);

		print "Extracted ramdisk contents to directory 'ramdisk'\n";
		$unpack_sucess = 1;
	}

	if ($unpack_sucess == 1) {
		print colored ("\nSuccessfully unpacked $extract.", 'green') . "\n";
	}
}

sub die_msg {
	die colored ("\n" . wrap("","","Error: $_[0]"), 'red') . "\n";
}

