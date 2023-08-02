%% Postprocessing Script for the Encoder Output Dynamic Test
%%  Microelectronic Circuits Centre Ireland (www.mcci.ie)
% 
%% 
% *Filename: *    encoderDynamicProcessing.m
%%                    
% *Written by: *  Anthony Wall
%% 
% *Created on:*  25th July 2023
% 
% *Revised on:*   -
% 
% 
% 
% *File Description:*
% 
%  Postprocessing for the Asynchronous Block
% 
% 
% 
% _* Copyright 2023 Anthony Wall*_

%% Initialisation Section

clearvars -except nch pch
global ON OFF fc T kb;

ON = 1;

OFF = 0;


fc = 10;

maxNumCompThreads(32);

set(groot, 'defaultAxesTickLabelInterpreter','latex');
set(groot, 'defaultLegendInterpreter','latex');
set(groot, 'defaultTextInterpreter','latex');

profile on

%% Parameter Declaration

% Configuration Switches
plotRaw			= 1; % Plot the raw time domain input data or not
plotFFT         = 1;
plotOutTime		= 0; % Plot the NUSDSP output data in time domain or not


% FFT Parameters
Nwindows = 8;
Frac_Overlap = inf;
N_FFTmax = 2^24;

% Metrics Parameters
NBW = 1e6; % Noise Bandwidth for SNR etc
f_NF = [100 500]*1e3; % Noisefloor frequency limits to estimate thermal noisefloor

% Postprocessing DSP Parameters
LSB_CORR = 0;

% Timecode File Readin Parameters
foldername = 'tmp';

datadir = strcat('../outputdata/', foldername, '/');


%% Reading in the metadata & Filenames

tmp = sprintf("%smetadata.csv", datadir);
metaData = readtable(tmp, 'Delimiter', ',', 'ReadVariableNames', true);

dataPoint = metaData.dataPoint;
Iin_pk = metaData.Iin_pk;
T_Q = metaData.T_Q;
T_inj = T_Q*66;
f_in = metaData.f_in;
I_DC = metaData.I_DC;

filenames = dir(strcat(datadir, '*.csv'));
for k = 1:length(filenames)
	tmp = regexp(filenames(k).name, '\d+\.csv'); % Removing the metadata file from filenames
	if(isempty(tmp))
		filenames(k) = [];
	end
end

%% Looping through the files
fc=fc+1;

%for runloop = 1:length(dataPoint)
for runloop = 10
    fprintf('Progress: %d/%d points\n\n', runloop, length(dataPoint));


    % Extracting the raw data from the data file
	encRaw = load(strcat(filenames(runloop).folder, '/', sprintf('%d', dataPoint(runloop)), '.csv'));
	
    	% Plotting the raw data as a sanity check
	if(plotRaw)
		figure(fc)
		clf
        hold on
		plot(0:length(encRaw)-1, encRaw, '-*')
		grid on
		title(sprintf('Edge timecounts for $I_{IN}^{pk} = %.3f \\mathrm{\\mu A}$', Iin_pk(runloop)*1e6))
		xlabel('Sample')
		ylabel('Time Encoded Count')
    end
    
    % Unwrapping the encoded output
    dEnc = diff(encRaw);
    wrapInds = find(dEnc < 0) + 1;
    encUnwrap = encRaw;
    for k = 1:length(wrapInds)
       encUnwrap(wrapInds(k):end) = encUnwrap(wrapInds(k):end) + (2^12);
    end
    
    if(plotRaw)
       figure(fc)
       plot(0:length(encUnwrap)-1, encUnwrap, '-o')
       legend('Wrapped', 'Unwrapped')
    end
    
    % Trimming the enc output to avoid huge data
    logNenc = floor(log2(max(encUnwrap)));
    encUnwrap(encUnwrap >= 1.05*min(2^logNenc, Nwindows*N_FFTmax)) = [];
    
    
    % Creating a time vector
    t = 0:T_Q(runloop):T_Q(runloop)*max(encUnwrap);
   
    
    % Creating an equivalent sampled output
    DFFout = zeros(size(t));
    DFFout(encUnwrap) = 1;
    
    % Trimming to nearest 2^N
    Nfft = floor(log2(length(t)));
    t(1:end-(2^Nfft)) = [];
    DFFout(1:end-(2^Nfft)) = [];
    
    % Plotting the equivalent sampled output
    if(plotOutTime)
       figure(fc+1)
       clf
       hold on
       %stairs(t, DFFout, '*-')
       stairs(t(1:1e4), movmean(DFFout(1:1e4), 50), '--')
       xlabel('Sampled Time $\mathrm{[s]}$')
       ylabel('Output')
       title('Effected Sampled Encoder Output')
       grid on
    end
    
    % Taking the FFT of the sampled output
	[Pout, f{runloop}] = pwelch(DFFout, hann((2^Nfft)/Nwindows), (2^Nfft)/Frac_Overlap, [], 1/T_Q(runloop), 'onesided');
    
    % Postprocessing the FFT to calculate performance metrics
    
    % Referring the PSD to the input amplitude
	Ind_in = NearestIndex(f{runloop}, f_in(runloop));
    Dout_f_dBc{runloop} = pow2db(Pout) - pow2db(Pout(Ind_in));

	% Calculating the power per bin by integrating over a rectangular bin
	df = f{runloop}(2)-f{runloop}(1);
	Pow_bin = Pout .* df;


	% Calculating the DC component & removing it from spectrum
		Pow_DC = sum(Pow_bin(1:4));
		I_DC(runloop) = sqrt(Pow_DC); %% Correct the scaling on this later
		Pow_bin(1:4) = 0;


	
	% Calculating the Signal Power & Removing it from the remaining spectrum
		
		Pow_in = Pow_bin(Ind_in) + sum(Pow_bin(Ind_in+(1:4))) + sum(Pow_bin(Ind_in-(1:4)));
		Pow_bin_in = Pow_bin(Ind_in); % Remembering the power at the centre bin which is used to calculate dBc 
		Iin_pk_fft(runloop) = sqrt(Pow_in) * sqrt(2)
		Pow_bin(Ind_in) = 0;
		Pow_bin(Ind_in+(1:4)) = 0;
		Pow_bin(Ind_in-(1:4)) = 0;


	% Calculating the Power in the first 10 Harmonics & Removing it from the
		% remainaing spectrum

		f_harm = [2 3 4 5 6 7 8 9 10 11] .* f_in(runloop);
		Ind_harm = NearestIndex(f{runloop}, f_harm);

		Pow_harm = 0;
		for k = 0:3
			Pow_harm = Pow_harm + sum(Pow_bin(Ind_harm)) + sum(Pow_bin(Ind_harm+k)) + sum(Pow_bin(Ind_harm-k));
		end
        Pow_H2 = Pow_bin(Ind_harm(1)) + sum(Pow_bin(Ind_harm(1)+(1:3))) + sum(Pow_bin(Ind_harm(1)-(1:3)));
        Pow_H3 = Pow_bin(Ind_harm(2)) + sum(Pow_bin(Ind_harm(2)+(1:3))) + sum(Pow_bin(Ind_harm(2)-(1:3)));
		Pow_bin(Ind_harm+(0:4)) = 0;
		Pow_bin(Ind_harm-(1:4)) = 0;


	% Calculating the RMS Noise
		Pow_noise = sum(Pow_bin(f{runloop}<NBW));
	

	% Calculating the average noise floor between the specified points in
    % f_NF
    	ind = f{runloop} >= f_NF(1) & f{runloop} <= f_NF(2); % Finding the indices that fall in the noise floor
    	Pbins_NF = Pow_bin(ind);
    	Pbins_NF(Pbins_NF == 0) = []; % Negating any indices where the power is zero - indicating that it has already been calculated in a harmonic etc
    	Pow_NF(runloop) = mean( 10*log10( Pbins_NF ) );
    	Pow_NF_dBc(runloop) = Pow_NF(runloop) - 10*log10(Pow_bin_in);
    	fprintf('When I_{IN}^{pk} = %.2f nA, NF = %.4fdBc\n', Iin_pk(runloop).*1e9, Pow_NF_dBc(runloop))


	% Calculating the THD = 10*log10(Pharm/Psig)
		THD(runloop) = 10*log10(Pow_harm / Pow_in)
        H2_over_H1(runloop) = 10*log10(Pow_H2 / Pow_in)
        H3_over_H1(runloop) = 10*log10(Pow_H3 / Pow_in)


	% Calculating the SNR = 10*log10(Psig/Pnoise)
		SNR(runloop) = 10*log10(Pow_in / Pow_noise)


	% Calculating the SNR = 10*log10(Psig / Pnoise+Pharm)
		SNDR(runloop) = 10*log10(Pow_in / (Pow_noise+Pow_harm))
    
    if(plotFFT)
       figure(fc+2)
       clf
       semilogx(f{runloop}, Dout_f_dBc{runloop})
       grid on
       title(sprintf('PSD Plot for $I_{IN}^{pk} = %.3f~\\mathrm{\\mu A}$', 1e6*Iin_pk(runloop)))
       xlabel('Frequency (Hz)')
       ylabel('PSD $\mathrm{[A/\surd Hz]}$')
	   set(gca, 'xscale', 'log')
       
    end
    
    
    
   
    
 end
fc=fc+1;

profile viewer