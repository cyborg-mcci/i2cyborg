%% Postprocessing Script for the Encoder Output Dynamic Test
%%  Microelectronic Circuits Centre Ireland (www.mcci.ie)
% 
%% 
% *Filename: *    encoderStaticProcessing.m
%%                    
% *Written by: *  Anthony Wall
%% 
% *Created on:*  19th September 2023
% 
% *Revised on:*   -
% 
% 
% 
% *File Description:*
% 
%  Postprocessing for Linearity Sweeps of the Asynchronous Block
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

% Timecode File Readin Parameters
foldername = 'B1C1_400MFlck_12uIbias';


datadir = strcat('../outputdata/linearENC/', foldername, '/');

%% Reading in the metadata & Filenames
