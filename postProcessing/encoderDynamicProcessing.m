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
plotOutTime		= 1; % Plot the NUSDSP output data in time domain or not

% Test Parameters
f_in = 100e3;
T_inj = 1/120e6;
T_Q = T_inj * 66;

% FFT Parameters
Nwindows = 1;
Frac_Overlap = inf;

% Metrics Parameters
NBW = 1e6; % Noise Bandwidth for SNR etc
f_NF = [100 500]*1e3; % Noisefloor frequency limits to estimate thermal noisefloor

% Postprocessing DSP Parameters
LSB_CORR = 0;

% Timecode File Readin Parameters
foldername = 'tmpout';

datadir = strcat('../outputdata/', foldername, '/');

%% Looping through the files
fc=fc+1;

for runloop = 1:length(filenames)
fprintf('Progress: %d/%d points\n\n', runloop, length(filenames));


% Extracting the raw data from the data file
	tmp = load(strcat(filenames(runloop).folder, '/', sprintf('%d', variables.DataPoint(runloop)), '.mat'));
	rawdata = tmp.simdata;
    
    
   
    
end