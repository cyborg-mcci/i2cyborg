%% Cyborg Channel Dynamic Sweep Generic Comparison
%%  Microelectronic Circuits Centre Ireland (www.mcci.ie)
% 
%% 
% *Filename: *    Dyn_sweep_generic_comp.m
%%                    
% *Written by: *  Anthony Wall
%% 
% *Created on:*  11th November 2021
% 
% *Revised on:*   -
% 
% 
% 
% *File Description:*
% 
%  Script to compare the Channel Dynamic sweep by taking the .mat files
%  created by the Dyn_Sweep_Plot.m file and plotting them on the same axes
% 
% 
% 
% _* Copyright 2021 Anthony Wall*_

%% Initialisation Section

clearvars -EXCEPT
global ON OFF s FigureCounter T kb fmin fmax FreqPoints wmax wmin w_test f;

ON = 1;

OFF = 0;


FigureCounter = 0;

%maxNumCompThreads(12);
set(groot, 'defaultAxesTickLabelInterpreter','latex');
set(groot, 'defaultLegendInterpreter','latex');
set(groot, 'defaultTextInterpreter','latex');

profile on



%% Parameter Declaration


% Physical Constants
T = 300.15;
kb = physconst('Boltzmann');
q = 1.602e-19;

% Quantisation Noise Model Parameters
N_Phases = 3;
N_Edges = 1;
Fs = 1e9;

% Thermal Noise Model Parameters
k_thn = sqrt(4.*kb.*T.*12)*0;
NBW = 1e6;

% Harmonic Prediction Model Parameters
 t_dead = 767e-12; % Fitting to measured results
 C_L = 60e-15; % Fitting to measured results

%t_dead = 120e-12; % Designed results
%C_L = 100e-15; % Designed Results

dV_ded = 0.502;
alpha = 1.0; % Derived from alpha = dV_ideal/dV_sim... This is a rouch average over input currents

% Input & Bias Parameters
Ibias = 3.2e-6;
Iin_pk_mdl = logspace(log10(10e-9), log10(100e-6), 101);

% Desired PSD Plot Point
Iin_pk_for_PSD = 50e-9;


%% Loading the file data

    


%filenames = {'ping_pong_initial_test', 'pingpong_40uABias', 'tmp'};

% filenames = {...
% 			'Ideal_Fs1Gsps_Fpfm12MHz', ...
% 			'Ideal_Fs1Gsps_Fpfm24MHz', ...
% 			'Ideal_Fs1Gsps_Fpfm48MHz', ...
% 			'Ideal_Fs1Gsps_Fpfm80MHz', ...
% 			'Ideal_Fs1Gsps_Fpfm120MHz', ...
% 			'Ideal_Fs1Gsps_Fpfm240MHz', ...
% 			'Ideal_Fs1Gsps_Fpfm480MHz', ...
% 			'Ideal_Fs1Gsps_Fpfm500MHz', ...
% 			'Ideal_Fs1Gsps_Fpfm504p2MHz', ...
% 			'Ideal_Fs1Gsps_Fpfm800MHz', ...
% 			'Ideal_Fs1Gsps_Fpfm1GHz', ...
% 			'Ideal_Fs1Gsps_Fpfm1p5GHz', ...
% 			'Ideal_Fs1Gsps_Fpfm1p9081GHz', ...
% 			'Ideal_Fs1Gsps_Fpfm3GHz', ...
% 			'Ideal_Fs1Gsps_Fpfm4p674GHz', ...
% 			'Ideal_Fs1Gsps_Fpfm10GHz', ...
% 			'Ideal_Fs1Gsps_Fpfm50GHz' ...
% 			};

% filenames = {'CH2_Ib12uA_LiOn' ...
% 			 'MASTER_CHAN_TT_27C_1p2V', ...
% 			 'MASTER_CHAN_FF_m40C_1p3V', ...
% 			 'MASTER_CHAN_SS_125C_1p1V' ...
% 			 };

filenames = {'B1C1_ringingDebug_Vref600mV', 'B1C1_ringingDebug_Vref6125mV', 'tmp'};







%filenames = {'tmp'};

for k = 1:length(filenames)
   tmp = load(filenames{k});
   PSD_data{k} = tmp.PSD_data;
end

% Comment out if simulation data is not present. Note simulation data must
% be last in order!!
%   PSD_data{end} = PSD_data{end}{1,1};
%  
%  [PSD_data{end}.Iin_pk, ind] = sort(PSD_data{end}.Ain);
%  %PSD_data{end}.Iin_pk  = PSD_data{end}.Iin_pk./10000;
%  PSD_data{end}.Iin_pk  = PSD_data{end}.Iin_pk;
%  PSD_data{end}.SNR = PSD_data{end}.SNR(ind);
%  PSD_data{end}.SNDR = PSD_data{end}.SNDR(ind);
%  PSD_data{end}.THD = PSD_data{end}.THD(ind);
%  PSD_data{end}.H2overH1 = PSD_data{end}.H2_over_H1(ind);
%  PSD_data{end}.H3overH1 = PSD_data{end}.H3_over_H1(ind);
%   for m = 1:length(PSD_data{end}.PSD.dB)
%       PSD_data{end}.PSD.dBc{m} = PSD_data{end}.PSD.dB{ind(m)}-61.541;
%       %PSD_data{end}.PSD.dBc{m} = PSD_data{end}.PSD.dBc{m} - PSD_data{end}.PSD.dBc{NearestIndex(PSD_data{end}.PSD.f{m}, 100e3)}
%       PSD_data{end}.PSD.f{m} = PSD_data{end}.PSD.f{ind(m)};
%   end

%% %%%%%%%%%%%%%%%%%% Model Calculation Section %%%%%%%%%%%%%%%%%%%%%%%%%%%%
% For a more in-depth look at the t_dead model, look at
% MATLAB/ADC_Modelling/CSROSC/CSROSC_HarmonicPredictor.m

[Iin_pk_mdl, C_L] = meshgrid(Iin_pk_mdl, C_L);

Ibias = Ibias .* ones(size(Iin_pk_mdl));

Ntay = 4;
%% Running the Harmonic Prediction Model

%% Using the t_active + t_dead model

f_actded = Iin_pk_mdl ./ (3.*t_dead.*Iin_pk_mdl + 3.*dV_ded.*C_L.*alpha);

%% Using the Taylor Series Approximation

syms beta gamma Iin_sym Ibias_sym td dV_sym C_L_sym alpha_sym

beta = 3*td;
gamma = 3*dV_sym*C_L_sym*alpha_sym;

f_cco_sym = 1/(beta + (gamma/Iin_sym));

f_cco_sym_taylor = taylor(f_cco_sym, Iin_sym, Ibias_sym, 'Order', Ntay);



% Substituting for Numeric Values
for k = 1:size(C_L,1)
    for m = 1:size(Iin_pk_mdl, 2)
        f_cco_taylor(k,m) = subs(f_cco_sym_taylor, ...
            {td, dV_sym, C_L_sym, alpha_sym, Ibias_sym}, {t_dead, dV_ded, C_L(k,m), alpha, Ibias(k,m)});
        
        f_cco_taylor(k,m) = subs(f_cco_sym_taylor, ...
            {td, dV_sym, C_L_sym, alpha_sym, Ibias_sym, Iin_sym}, {t_dead, dV_ded, C_L(k,m), alpha, Ibias(k,m), Iin_pk_mdl(k,m)});

    end
end

    f_cco_taylor = double(f_cco_taylor);
	
	coef = coeffs(f_cco_sym_taylor, Iin_sym);

%% Predicting the Harmonic Levels

for k = 1:size(C_L,1)
    for m = 1:size(Iin_pk_mdl, 2)
        
        a_0(k,m) = subs(coef(1), {td, dV_sym, C_L_sym, alpha_sym, Ibias_sym, Iin_sym},...
                                {t_dead, dV_ded, C_L(k,m), alpha, Ibias(k,m), Iin_pk_mdl(k,m)});

        a_1(k,m) = subs(coef(2), {td, dV_sym, C_L_sym, alpha_sym, Ibias_sym, Iin_sym},...
                                {t_dead, dV_ded, C_L(k,m), alpha, Ibias(k,m), Iin_pk_mdl(k,m)}); 
                            
        a_2(k,m) = subs(coef(3), {td, dV_sym, C_L_sym, alpha_sym, Ibias_sym, Iin_sym},...
                                {t_dead, dV_ded, C_L(k,m), alpha, Ibias(k,m), Iin_pk_mdl(k,m)});
                            
        a_3(k,m) = subs(coef(4), {td, dV_sym, C_L_sym, alpha_sym, Ibias_sym, Iin_sym},...
                                {t_dead, dV_ded, C_L(k,m), alpha, Ibias(k,m), Iin_pk_mdl(k,m)});
    end
end

a_0 = double(a_0);
a_1 = double(a_1);
a_2 = double(a_2);
a_3 = double(a_3);

A_pk_fund = Iin_pk_mdl .* (a_1 + 0.75.*a_3.*Iin_pk_mdl.^2);
A_pk_H2 = abs(0.5.*a_2.*Iin_pk_mdl.^2);
A_pk_H3 = 0.25.*a_3.*Iin_pk_mdl.^3;

H2_over_fund_dBc = 20*log10(A_pk_H2./A_pk_fund);
H3_over_fund_dBc = 20*log10(A_pk_H3./A_pk_fund);


% Estimating THD
THD_mdl = 20*log10(sqrt(A_pk_H2.^2 + A_pk_H3.^2) ./ A_pk_fund);


%% Estimating Thermal Noise (to a first order)

i_thn = k_thn .* sqrt(NBW) .* sqrt(Ibias);
SNR_mdl = 20.*log10(Iin_pk_mdl./i_thn);


%% Estimating Quantisation Noise (to a first order)
f_mdl = linspace(0, NBW, 1e3);

Kcco = 1./(C_L.*N_Phases.*dV_ded.*alpha);

for k = 1:length(f_mdl)
    inq_psd(:,:,k) = 2*pi.*f_mdl(k) ./ (sqrt(12).*sqrt(Fs).*Kcco.*N_Phases.*N_Edges);
end

for k = 1:size(C_L,1)
    for m = 1:size(Iin_pk_mdl, 2)
        inq(k,m) = sqrt(trapz(f_mdl, inq_psd(k,m,:).^2));
    end
end

SNQR_mdl = 20.*log10(Iin_pk_mdl ./ inq*sqrt(2));

%% Estimating SNDR

SNDR_mdl = 20.* log10(Iin_pk_mdl) - 10.*log10(inq.^2 + i_thn.^2 + db2pow(THD_mdl).*(Iin_pk_mdl.^2));
  
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%




%% Plotting the SNDR 

%FigureCounter = FigureCounter + 1;
figure(1)
clf
hold on
for k = 1:length(PSD_data)
    plt(k) = plot(PSD_data{k}.Iin_pk, PSD_data{k}.SNDR, 'linewidth', 2);
    LegendString{k} = strrep(sprintf('SNDR: %s', filenames{k}), '_', '\_');
end

    plt(length(plt)+1) = plot(Iin_pk_mdl, SNDR_mdl, ':', 'linewidth', 3.5);
    LegendString{length(LegendString)+1} = '$t_{dead}$ Model';

legend(LegendString, 'location', 'northwest')
grid on
xlabel('Peak Input Current ($I_{in}^{pk}$) $\mathrm{[A^{pk}]}$')
ylabel('SNDR $\mathrm{[dB]}$')
title('Plot of SNDR vs. Input Amplitude')
set(gca, 'Xscale', 'log')
set(gca, 'Yscale', 'linear')
%set(gca, 'xticklabels', {'$1n$', '$10n$', '$100n$', '$1\mu$', '$10\mu$'})
%darkBackground(gcf)
set(gca, 'fontsize', 14)
% ExportFilename = 'Dynamic_CH1_vs_CH2.pdf';
% export_fig(ExportFilename, '-pdf', '-transparent', gcf)

%% Plotting specified PSDs overlayed


clear LegendString

for k = 1:length(PSD_data)
    ind(k) = NearestIndex(PSD_data{k}.Iin_pk, Iin_pk_for_PSD);
end

%FigureCounter = FigureCounter + 1;
figure(2)
clf
hold on
for k = 1:length(PSD_data)
   plt(k) = plot(PSD_data{k}.PSD.f{ind(k)}, PSD_data{k}.PSD.dBc{ind(k)});
   LegendString{k} = strrep(sprintf('SNDR: %s', filenames{k}), '_', '\_');
end
legend(LegendString)
grid on
xlabel('Frequency ($f$) $\mathrm{[Hz]}$')
ylabel('PSD $\mathrm{[dBc]}$')
title(sprintf('PSD Plots for the point closest to $I_{IN}^{pk} = %.1f ~\\mathrm{nA}$', Iin_pk_for_PSD*1e9))
set(gca, 'Xscale', 'log')
set(gca, 'Yscale', 'linear')
%darkBackground(gcf)
set(gca, 'fontsize', 14)



%% Plotting the HD2 and HD3
clear LegendString
%FigureCounter = FigureCounter + 1;
figure(3)
clf
hold on

 for k = 1:length(PSD_data)
     if isfield(PSD_data{k}, 'Pow_NF_dBc')
        plt((3*k-2):3*k) = plot(PSD_data{k}.Iin_pk, PSD_data{k}.H2overH1, PSD_data{k}.Iin_pk, PSD_data{k}.H3overH1, PSD_data{k}.Iin_pk, PSD_data{k}.Pow_NF_dBc, 'linewidth', 2);
        if exist('LegendString', 'var')
            LegendString{length(LegendString)+1} = strrep(sprintf('HD2: %s', filenames{k}), '_', '\_');
        else
            LegendString{1} = strrep(sprintf('HD2: %s', filenames{k}), '_', '\_');
        end
        LegendString{length(LegendString)+1} = strrep(sprintf('HD3: %s', filenames{k}), '_', '\_');
        LegendString{length(LegendString)+1} = strrep(sprintf('Noisefloor: %s', filenames{k}), '_', '\_');
     else
         plt(length(plt)+1:length(plt)+2) = plot(PSD_data{k}.Iin_pk, PSD_data{k}.H2overH1, PSD_data{k}.Iin_pk, PSD_data{k}.H3overH1, 'linewidth', 2);
        if exist('LegendString', 'var')
            LegendString{length(LegendString)+1} = strrep(sprintf('HD2: %s', filenames{k}), '_', '\_');
        else
            LegendString{1} = strrep(sprintf('HD2: %s', filenames{k}), '_', '\_');
        end
        LegendString{length(LegendString)+1} = strrep(sprintf('HD3: %s', filenames{k}), '_', '\_');
     end
 end
 
 
plt(length(plt)+(1:2)) = plot(Iin_pk_mdl, H2_over_fund_dBc, ':', Iin_pk_mdl, H3_over_fund_dBc, ':', 'linewidth', 3.5);
LegendString{length(LegendString)+1} = 'HD2: Modelled';
LegendString{length(LegendString)+1} = 'HD3: Modelled';

grid on
legend(LegendString, 'location', 'SouthWest')
xlabel('$I_{in}^{pk}$ (A)')
ylabel('dB')
title('Plot of HD2 and HD3 vs. Input Amplitude')
set(gca, 'Xscale', 'log')
%set(gca, 'xticklabels', {'$1n$', '$10n$', '$100n$', '$1\mu$', '$10\mu$'})
set(gca, 'Yscale', 'linear')
%darkBackground(gcf)
set(gca, 'fontsize', 14)


% ExportFilename = 'MRCAP_CHAN_StatLin_Sim_vs_meas.pdf';
% export_fig(ExportFilename, '-pdf', '-transparent', gcf)

