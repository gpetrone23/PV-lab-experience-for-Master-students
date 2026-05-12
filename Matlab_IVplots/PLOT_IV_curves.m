clear all 
close all

filename_V = {'IVscanG75W.csv'; 'IVscanG150W.csv'; 'IVscanG225W.csv'; 'IVscanG375W.csv'};

figure(1); 

% Variables to track global maximums for consistent axis limits
maxV = 0; maxI = 0; maxP = 0;

for ii = 1:length(filename_V)
    filename = filename_V{ii};
    data = readtable(filename);

    x = data.Vpan; 
    y = data.Ipan;
    z = data.Ppan;
    
    % Update maximum values found across all files
    maxV = max(maxV, max(x));
    maxI = max(maxI, max(y));
    maxP = max(maxP, max(z));
    cleanName = strrep(filename, 'IVscan', '');
    cleanName = strrep(cleanName, 'G', 'G=');
    cleanName = strrep(cleanName, '.csv', '');
    cleanName = strrep(cleanName, 'W', ' W/m^2');

    % --- Subplot 1: I-V Characteristics ---
    subplot(1, 2, 1); hold on
    plot(x, y, 'LineWidth', 2, 'DisplayName', cleanName); 
    
    % --- Subplot 2: P-V Characteristics ---
    subplot(1, 2, 2); hold on
    plot(x, z, 'LineWidth', 2, 'DisplayName', cleanName); 
end

% --- Final Styling for Subplot 1 (I-V) ---
subplot(1, 2, 1);
title('I-V Characteristics', 'FontSize', 16);
xlabel('Voltage (V)', 'FontSize', 14);
ylabel('Current (A)', 'FontSize', 14);
grid on; box on;
set(gca, 'FontSize', 16);
legend('show', 'Location', 'southwest', 'FontSize', 14);
% Set limits: [min, max]
xlim([0, maxV * 1.05]); % 5% margin
ylim([0, maxI * 1.05]);

% --- Final Styling for Subplot 2 (P-V) ---
subplot(1, 2, 2);
title('P-V Characteristics', 'FontSize', 16);
xlabel('Voltage (V)', 'FontSize', 14);
ylabel('Power (W)', 'FontSize', 14);
grid on; box on;
set(gca, 'FontSize', 16);
legend('show', 'Location', 'northwest', 'FontSize', 14);
% Set limits
xlim([0, maxV * 1.05]); 
ylim([0, maxP * 1.05]);

sgtitle('Photovoltaic Panel Analysis', 'FontSize', 20, 'FontWeight', 'bold');
