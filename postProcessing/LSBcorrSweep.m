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
plotRaw			= 0; % Plot the raw time domain input data or not
plotFFT         = 1;
plotOutTime		= 0; % Plot the NUSDSP output data in time domain or not


% FFT Parameters
Nwindows = 4;
Frac_Overlap = inf;
N_FFTmax = 2^26;

% Metrics Parameters
NBW = 1e6; % Noise Bandwidth for SNR etc
f_NF = [100 500]*1e3; % Noisefloor frequency limits to estimate thermal noisefloor

% Postprocessing DSP Parameters
LSB_CORR = 0:30;
dataPointSel = 188;

% Timecode File Readin Parameters
foldername = 'B1C1_stabFix_Flk1p51G_Ib4u_vref1p4';


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

for runloop = 1:length(LSB_CORR)

%for runloop = 10
    fprintf('Progress: %d/%d points, LSBcorr = %d\n\n', runloop, length(LSB_CORR), LSB_CORR(runloop));


    % Extracting the raw data from the data file
	encRaw = load(strcat(filenames(dataPointSel).folder, '/', sprintf('%d', dataPoint(dataPointSel)), '.csv'));
	
    	% Plotting the raw data as a sanity check
	if(plotRaw)
		figure(fc)
		clf
        hold on
		plot(0:length(encRaw)-1, encRaw, '-*')
		grid on
		title(sprintf('Edge timecounts for $I_{IN}^{pk} = %.3f \\mathrm{\\mu A}$', Iin_pk(dataPointSel)*1e6))
		xlabel('Sample')
		ylabel('Time Encoded Count')
        
        figure(fc+1)
        clf
        hist(encRaw, 4096);
        title('Count Distribution Histogram')
        grid on
        
    end
    
    % Unwrapping the encoded output
    dEnc = diff(encRaw);
    wrapInds = find(dEnc < 0) + 1;
    wrapToAdd = 4096*(1:length(wrapInds));
    encUnwrap = encRaw;
    for k = 1:length(wrapInds)
        if k < length(wrapInds)
            encUnwrap(wrapInds(k):wrapInds(k+1)-1) = encUnwrap(wrapInds(k):wrapInds(k+1)-1) + wrapToAdd(k);
        else
            encUnwrap(wrapInds(k):end) = encUnwrap(wrapInds(k):end) + wrapToAdd(k);
        end
        
    end
    
    if(plotRaw)
       figure(fc)
       plot(0:length(encUnwrap)-1, encUnwrap, '-o')
       legend('Wrapped', 'Unwrapped')
       
       figure(fc+2)
       clf
       plot(0:length(encUnwrap)-2, diff(encUnwrap), '*-');
       grid on
       title('Difference Between Subsequent Counts')
    end
    
    % Performing Nonlinearity Correction
    LSB_CORR_to_subtract = (0:length(encUnwrap)-1) .* LSB_CORR(runloop);
	count_corr = encUnwrap - LSB_CORR_to_subtract';
    
    % Trimming the enc output to avoid huge data
    logNenc = floor(log2(max(count_corr)));
    %encUnwrap(encUnwrap >= 1.05*min(2^logNenc, Nwindows*N_FFTmax)) = [];
    count_corr(count_corr < 1) = []; % trimming negative results since time starts at index 1 (t=0)
    
    % Creating a time vector
    t = 0:T_Q(runloop):T_Q(runloop)*max(count_corr);
   
    
    % Creating an equivalent sampled output
    DFFout = zeros(size(t));
    DFFout(count_corr) = 1;
    
    % Trimming to nearest 2^N
    Nfft = floor(log2(length(t)));
    t(1:end-(Nwindows*N_FFTmax)) = [];
    DFFout(1:end-(Nwindows*N_FFTmax)) = [];
    
    % Plotting the equivalent sampled output
    if(plotOutTime)
       figure(fc+3)
       clf
       hold on
       %stairs(t, DFFout, '*-')
       stairs(t(1:1e4), movmean(DFFout(1:1e4), 50), '--')
       xlabel('Sampled Time $\mathrm{[s]}$')
       ylabel('Output')
       title('Effective Sampled Encoder Output')
       grid on
    end
    
    % Taking the FFT of the sampled output
	[Pout, f] = pwelch(DFFout, blackmanharris((N_FFTmax)/Nwindows), (N_FFTmax)/Frac_Overlap, [], 1/T_Q(runloop), 'onesided');
    
    % Postprocessing the FFT to calculate performance metrics
    metrics{runloop} = calculateFFTMetrics(f, Pout, f_in(runloop), NBW, f_NF);
    metrics{runloop}


    
    if(plotFFT)
       figure(fc+4)
       clf
       semilogx(metrics{runloop}.f, metrics{runloop}.Dout_f_dBc)
       grid on
       title(sprintf('PSD Plot for $I_{IN}^{pk} = %.3f~\\mathrm{\\mu A}, LSB_{CORR} = %d$', 1e6*Iin_pk(dataPointSel), LSB_CORR(runloop)))
       xlabel('Frequency (Hz)')
       ylabel('PSD $\mathrm{[A/\surd Hz]}$')
	   set(gca, 'xscale', 'log')
       
    end
    
    
   
    
 end
fc=fc+4;

%% Adding Metadata to the metrics
    saveData.filename = foldername;
    saveData.variables = metaData;
    saveData.Nwindows = Nwindows;
    saveData.Nfft = Nfft;
    %saveData.metrics = metrics;
    saveData.LSB_CORR = LSB_CORR

%% Plotting the SNDR 
for k = 1:length(metrics)
   saveData.I_DC(k) =  metrics{k}.I_DC;
   saveData.Iin_pk_fft(k) = metrics{k}.Iin_pk_fft;
   saveData.Pow_NF_dBc(k) = metrics{k}.Pow_NF_dBc;
   saveData.H2_over_H1(k) = metrics{k}.H2_over_H1;
   saveData.H3_over_H1(k) = metrics{k}.H3_over_H1;
   saveData.THD(k) = metrics{k}.THD;
   saveData.SNR(k) = metrics{k}.SNR;
   saveData.SNDR(k) = metrics{k}.SNDR;
   
   %saveData.f{k} = metrics{k}.f;
   %saveData.Dout_f_dBc{k} = metrics{k}.Dout_f_dBc;
   
   
   
end

PSD_SaveName = inputdlg('Enter the PSD file Save Name');
if strcmp(PSD_SaveName{1}, 'same')
    save(foldername, 'saveData')
else
    save(PSD_SaveName{1}, 'saveData')
end




fc=fc+1
figure(fc)
clf
plot(LSB_CORR, saveData.SNDR, '-*', LSB_CORR, saveData.SNR, LSB_CORR, -saveData.THD, LSB_CORR, -saveData.H2_over_H1, LSB_CORR, -saveData.H3_over_H1);
grid on
legend('SNDR', 'SNR', '-THD', 'HD2', 'HD3')
xlabel('Peak Input Current ($I_{in}^{pk}$) $\mathrm{[A^{pk}]}$')
ylabel('$\mathrm{[dB]}$')
set(gca, 'Xscale', 'log')
set(gca, 'Yscale', 'linear')
set(gca, 'fontsize', 14)






profile viewer