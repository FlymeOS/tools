#!/usr/bin/perl

#
#
# Change history:
#   - add support mt6752/mt6732/mt6595 by cofface 20150127
#

use v5.14;
use warnings;
use Cwd;
use Compress::Zlib;
use Term::ANSIColor;
use FindBin qw($Bin);
use File::Basename;
use Text::Wrap;

my $dir = getcwd;

my $version = "mtk-unpack script by cofface 20150813\n";
my $usageMain = "repack-MTK.pl <COMMAND ...> <outfile>\n  Repacks MTK boot, recovery\n\n";
my $usage = $usageMain;

print colored ("$version", 'bold blue') . "\n";
die "Usage: $usage" unless $ARGV[0] && $ARGV[1] && $ARGV[2];

if ($ARGV[0] eq "-boot" || $ARGV[0] eq "-recovery") {
	if ($ARGV[1] eq "--debug") {
		die "Usage: $usage" unless $ARGV[3] && $ARGV[4] && !$ARGV[5];
	} else {
		die "Usage: $usage" unless $ARGV[3] && !$ARGV[4];
		splice (@ARGV, 1, 0, "--normal"); 
	}
	repack_boot();
} else {
	die "Usage: $usage";
}

sub clean_files {
#clean kernel args.txt ramdisk
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

sub repack_boot {
	my ($type, $mode, $kernel, $ramdiskdir, $outfile) = @ARGV;
	$type =~ s/^-//;
	my $debug_mode = ($mode =~ /debug/ ? 1 : 0);
	$ramdiskdir =~ s/\/$//;
	my $ramdiskfile = "ramdisk-new.cpio.gz";
	my $signature = ($type eq "boot" ? "ROOTFS" : "RECOVERY");
	my %args = (base => "0x10000000", kernel_offset => "0x00008000", ramdisk_offset => "0x01000000", second_offset => "0x00f00000", tags_offset => "0x00000100", pagesize => 2048, board => "", cmdline => "");

	die_msg("kernel file '$kernel' not found!") unless (-e $kernel);
	chdir $ramdiskdir or die_msg("directory '$ramdiskdir' not found!");

	foreach my $tool ("find", "cpio", "gzip") {
		die_msg("'$tool' binary not found! Double check your environment setup.")
			if system ("command -v $tool >/dev/null 2>&1");
	}
	print "Repacking $type image...\n";
	if ($debug_mode) {
		print colored ("\nRamdisk repack command:", 'yellow') . "\n";
		print "'find . | cpio -o -H newc | gzip > $dir/$ramdiskfile'\n\n";
	}
	print "Ramdisk size: ";
	system ("find . | cpio -o -H newc | gzip > $dir/$ramdiskfile");

	chdir $dir or die "\n$ramdiskdir $!";;

	open (RAMDISKFILE, $ramdiskfile)
		or die_msg("couldn't open ramdisk file '$ramdiskfile'!");
	my $ramdisk;
	while (<RAMDISKFILE>) {
		$ramdisk .= $_;
	}
	close (RAMDISKFILE);

	# generate the header according to the ramdisk size
	my $sizeramdisk = length($ramdisk);
	my $header = gen_header($signature, $sizeramdisk);

	# attach the header to ramdisk
	my $newramdisk = $header . $ramdisk;

	if ($debug_mode) {
		open (HEADERFILE, ">ramdisk-new.header")
			or die_msg("couldn't create MTK header file 'ramdisk-new.header'!");
		binmode (HEADERFILE);
		print HEADERFILE $header or die;
		close (HEADERFILE);
	} elsif (-e "ramdisk-new.header") {
		system ("rm ramdisk-new.header");
	}
	open (RAMDISKFILE, ">temp-$ramdiskfile")
		or die_msg("couldn't create repacked ramdisk file 'temp-$ramdiskfile'!");
	binmode (RAMDISKFILE);
	print RAMDISKFILE $newramdisk or die;
	close (RAMDISKFILE);
	
	# load extra args needed for creating the output file
	my $argsfile = $kernel;
	$argsfile =~ s/kernel/args.txt/;
	my @extrargs;
	if (-e $argsfile) {
		open(ARGSFILE, $argsfile)
			or die_msg("couldn't open extra args file '$argsfile'!");
		while (<ARGSFILE>) {
			if ($_ =~ /^\--(\w+) (.+)$/) {
				if (exists $args{$1}) {
					push (@extrargs, $_);
					$args{$1} = $2;
				}
			}
		}
		close (ARGSFILE);
		chomp (@extrargs);
	} else {
		print colored ("\nWarning: file containing extra arguments was not found! The $type image will be repacked using default base address, kernel and ramdisk offsets (as shown bellow).", 'yellow') . "\n";
	}

	# print build information (only in normal mode)
	if (!$debug_mode) {
		print colored ("\nBuild information:\n", 'cyan') . "\n";
		print colored (" Base address and offsets:\n", 'cyan') . "\n";
		printf ("  Base address:\t\t\t%s\n", $args{"base"});
		printf ("  Kernel offset:\t\t%s\n", $args{"kernel_offset"});
		printf ("  Ramdisk offset:\t\t%s\n", $args{"ramdisk_offset"});
		printf ("  Second stage offset:\t\t%s\n", $args{"second_offset"});
		printf ("  Tags offset:\t\t\t%s\n\n", $args{"tags_offset"});
		print colored (" Other:\n", 'cyan') . "\n";
		printf ("  Page size (bytes):\t\t%s\n", $args{"pagesize"});
		printf ("  ASCIIZ product name:\t\t'%s'\n", $args{"board"});
		printf ("  Command line:\t\t\t'%s'\n", $args{"cmdline"});
	}

	# create the output file
	my $tool = "mkbootimg" . (($^O eq "cygwin") ? ".exe" : (($^O eq "darwin") ? ".osx" : ""));
	die_msg("couldn't execute '$tool' binary!\nCheck if file exists or its permissions.")
		unless (-x "$Bin/$tool");
	if ($debug_mode) {
		print colored ("\nBuild $type image command:", 'yellow') . "\n";
		print "'$tool --kernel $kernel --ramdisk temp-$ramdiskfile @extrargs -o $outfile'\n";
	}
	system ("$Bin/$tool --kernel $kernel --ramdisk temp-$ramdiskfile @extrargs -o $outfile");

	# cleanup
	unlink ($ramdiskfile) or die $! unless ($debug_mode);
	system ("rm temp-$ramdiskfile");

	if (-e $outfile) {
		print colored ("\nSuccessfully repacked $type image into '$outfile'.", 'green') . "\n";
		#clean_files();
	}
}

sub gen_header {
	my ($header_type, $length) = @_;

	return pack('a4 L a32 a472', "\x88\x16\x88\x58", $length, $header_type, "\xFF"x472);
}

sub png_to_rgb565 {
	my $filename = $_[0] =~ s/.png$//r;
	my ($rgb565_data, $data, @encoded);

	# convert png into raw rgb (rgb888)
	system ("convert -depth 8 $filename.png rgb:$filename.raw");

	# convert raw rgb (rgb888) into rgb565
	open (RAWFILE, "$filename.raw")
		or die_msg("couldn't open temporary image file '$filename.raw'!");
	binmode (RAWFILE);
	while (read (RAWFILE, $data, 3) != 0) {
		@encoded = unpack('C3', $data);
		$rgb565_data .= pack('S', (($encoded[0] >> 3) << 11) | (($encoded[1] >> 2) << 5) | ($encoded[2] >> 3));
	}
	close (RAWFILE);

	# cleanup
	system ("rm $filename.raw");

	return $rgb565_data;
}

sub die_msg {
	die colored ("\n" . wrap("","       ","Error: $_[0]"), 'red') . "\n";
}
