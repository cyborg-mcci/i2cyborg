function metrics = calculateFFTMetrics(f, Psig, f_in, NBW, f_NF)



	% Referring the PSD to the input amplitude
	Ind_in = NearestIndex(f, f_in);
	

	Dout_f_dBc = pow2db(Psig) - pow2db(Psig(Ind_in));

	% Calculating the power per bin by integrating over a rectangular bin
	df = f(2)-f(1);
	Pow_bin = Psig .* df;


	% Calculating the DC component & removing it from spectrum
		Pow_DC = sum(Pow_bin(1:4));
		I_DC = sqrt(Pow_DC); %% Correct the scaling on this later
		Pow_bin(1:4) = 0;


	
	% Calculating the Signal Power & Removing it from the remaining spectrum
		
		Pow_in = Pow_bin(Ind_in) + sum(Pow_bin(Ind_in+(1:4))) + sum(Pow_bin(Ind_in-(1:4)));
		Pow_bin_in = Pow_bin(Ind_in); % Remembering the power at the centre bin which is used to calculate dBc 
		Iin_pk_fft = sqrt(Pow_in) * sqrt(2);
		Pow_bin(Ind_in) = 0;
		Pow_bin(Ind_in+(1:4)) = 0;
		Pow_bin(Ind_in-(1:4)) = 0;


	% Calculating the Power in the first 10 Harmonics & Removing it from the
		% remainaing spectrum

		f_harm = [2 3 4 5 6 7 8 9 10 11] .* f_in;
		Ind_harm = NearestIndex(f, f_harm);

		
        Pow_harm = sum(Pow_bin(Ind_harm));
		for k = 1:3
			Pow_harm = Pow_harm + sum(Pow_bin(Ind_harm+k)) + sum(Pow_bin(Ind_harm-k));
		end
        Pow_H2 = Pow_bin(Ind_harm(1)) + sum(Pow_bin(Ind_harm(1)+(1:3))) + sum(Pow_bin(Ind_harm(1)-(1:3)));
        Pow_H3 = Pow_bin(Ind_harm(2)) + sum(Pow_bin(Ind_harm(2)+(1:3))) + sum(Pow_bin(Ind_harm(2)-(1:3)));
		Pow_bin(Ind_harm+(0:3)) = 0;
		Pow_bin(Ind_harm-(1:3)) = 0;


	% Calculating the RMS Noise
		Pow_noise = sum(Pow_bin(f<NBW));
	

	% Calculating the average noise floor between the specified points in
    % f_NF
    	ind = f >= f_NF(1) & f <= f_NF(2); % Finding the indices that fall in the noise floor
    	Pbins_NF = Pow_bin(ind);
    	Pbins_NF(Pbins_NF == 0) = []; % Negating any indices where the power is zero - indicating that it has already been calculated in a harmonic etc
    	Pow_NF = mean( 10*log10( Pbins_NF ) );
    	Pow_NF_dBc= Pow_NF - 10*log10(Pow_bin_in);
    	%fprintf('When I_{IN}^{pk} = %.2f nA, NF = %.4fdBc\n', Iin_pk*1e9, Pow_NF_dBc)


	% Calculating the THD = 10*log10(Pharm/Psig)
		THD = 10*log10(Pow_harm / Pow_in);
        H2_over_H1 = 10*log10(Pow_H2 / Pow_in);
        H3_over_H1 = 10*log10(Pow_H3 / Pow_in);


	% Calculating the SNR = 10*log10(Psig/Pnoise)
		SNR = 10*log10(Pow_in / Pow_noise);


	% Calculating the SNR = 10*log10(Psig / Pnoise+Pharm)
		SNDR = 10*log10(Pow_in / (Pow_noise+Pow_harm));

	% Packing the output struct
		metrics.I_DC = I_DC;
		metrics.Iin_pk_fft = Iin_pk_fft;
		metrics.Pow_NF_dBc = Pow_NF_dBc;
		metrics.THD = THD;
		metrics.H2_over_H1 = H2_over_H1;
		metrics.H3_over_H1 = H3_over_H1;
		metrics.SNR = SNR;
		metrics.SNDR = SNDR;
		metrics.f = f;
		metrics.Dout_f_dBc = Dout_f_dBc;



end