import nearestPrime as nPrime

if __name__ == "__main__":
    # First figure out the desired input frequency
    try:
        f_in_des = float(input("Enter the desired Input Frequency in kHz: "))*1e3
    except Exception: 
        print("Invalid Input Frequency")
        exit

    # Prompt for T_Q or Flock
    try:
        tmp = float(input("Enter either the Locking frequency in Hz or the T_Q in s: "))

        if tmp < 1: 
            T_Q = tmp
            F_s = 1/T_Q
            print("F_lock = {:.6f} MHz".format(1e-6/(T_Q*66)))

        else:
            T_Q = 1/(66*tmp)
            F_s = 1/T_Q
            print("T_Q = {:.3f} ps".format(T_Q*1e12))
    except Exception: 
        print("Invalid Sampling Parameter")
        exit

    # Prompt for the Number of FFT Samples
    try:
        nSamp = 2**(int(input("Enter the number of FFT samples: 2^")))
    except Exception: 
        print("Invalid Number of samples")
        exit

    # Prompt for the number of averaged FFT windows
    try:
        nWindows = int(input("Enter the number of averaged FFT windows: "))
    except Exception: 
        print("Invalid Number of windows")
        exit

    # Prompt for the number of LSBs to correct
    try:
        LSBcorr = int(input("Enter the number of LSBs to Correct: "))
    except Exception: 
        print("Invalid Number of Correction LSBs")
        exit

    # Prompt the expected K_CCO
    try:
        K_cco = float(input("Enter the K_cco in MHz/uA: "))*1e12
    except Exception: 
        print("Invalid K_cco")
        exit

    # Prompt the expected dead time
    try:
        t_dead = float(input("Enter the expected t_dead in ps: "))*1e-12
    except Exception: 
        print("Invalid dead time")
        exit
    
    # Prompt the Ibias
    try:
        I_bias = float(input("Enter the I_bias in uA: "))*1e-6
    except Exception: 
        print("Invalid bias current")
        exit

    # Calculate the effective K_cco and number of pulses
    K_ccro_eff = K_cco / (1 + 2*t_dead*K_cco*I_bias)
    T_sim = T_Q * (nSamp-1)
    nPulses = T_sim * K_ccro_eff * I_bias

    # Calculate the right number of input cycles
    mCyc = nPrime.nearestPrime( (f_in_des * T_Q) * ((nSamp/nWindows) +  (nPulses*LSBcorr)) )
    f_in = mCyc / ( ( (nSamp/nWindows) + (nPulses*LSBcorr)) * T_Q )

    
        


    