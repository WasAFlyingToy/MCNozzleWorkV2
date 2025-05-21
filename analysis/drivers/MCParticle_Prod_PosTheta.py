import pyLCIO
import ROOT
import glob
import math

# Set up some options
max_events = -1

# Gather input files
fnames = [
    "/scratch/MCNozzleWork/simulation/mumu_H_bb_100Events/NoBlackhole/mumu_H_bb_100E.slcio",
    "/scratch/MCNozzleWork/simulation/mumu_H_bb_100Events/full_KZ_v1_4/mumu_H_bb_100E_TIP_KZv1_4_FULL.slcio",
    "/scratch/MCNozzleWork/simulation/mumu_H_bb_100Events/full_KZ_v1_4-3/mumu_H_bb_100E_TIP_KZv1_4-3_FULL.slcio",
    "/scratch/MCNozzleWork/simulation/mumu_H_bb_100Events/full_BH/mumu_H_bb_100E_BLACKHOLE_NOZZLE.slcio"
]

# names for each file
names = [
    "Default Geometry",
    "Blackhole 4cm deep",
    "Blackhole 4cm Nozzle, 3cm Shaft",
    "Full Nozzle Blackhole"
]

# Set up histograms
hists = {}
colors = [ROOT.kOrange, ROOT.kAzure+7, ROOT.kGreen+2, ROOT.kRed+2] # colors for histograms

# Loop over files to create histograms
for idx, f in enumerate(fnames):
    hist_name = f"MCParticle_Pos_Theta_{idx}"
    hists[hist_name] = ROOT.TH1F(hist_name, "", 50, 0, math.pi)

# Loop over events
event_count = 0
for idx, f in enumerate(fnames):
    reader = pyLCIO.IOIMPL.LCFactory.getInstance().createLCReader()
    reader.open(f)

    for event in reader:
        if max_events > 0 and event_count >= max_events:
            break
        if event_count % 100 == 0:
            print(f"Processing event {event_count} for {names[idx]}.") # Print out progress for checking purposes

        # Get the collections we care about
        collection = event.getCollection("MCParticle") 

        # Loop over the hits and fill histograms
        for p in collection:
            vertex = p.getVertex() # Get the vertex position
            x, y, z = vertex[0], vertex[1], vertex[2] # Get the x, y, z components of the vertex position
            radius = math.sqrt(x**2 + y**2 + z**2) # Calculate the radius of the vertex position

            # Check if radius is not zero to avoid division by zero
            if radius != 0:
                theta = math.acos(z / radius)
                hist_name = f"MCParticle_Pos_Theta_{idx}"
                hists[hist_name].Fill(theta)

        event_count += 1

    reader.close()

# Make plots
ROOT.gStyle.SetOptStat(0)
c = ROOT.TCanvas("c", "c", 2000, 1600) # canvas size

# margins to leave space for axis titles
c.SetLeftMargin(0.2)  # % of the canvas width
c.SetRightMargin(0.2)  # % of the canvas width
c.SetBottomMargin(0.1)  # % of the canvas height
c.SetTopMargin(0.1)  # % of the canvas height

# log scale for y-axis
c.SetLogy()

# histograms with different colors
legend = ROOT.TLegend(0.7, 0.7, 0.9, 0.9)
for idx, hist_name in enumerate(hists):
    hists[hist_name].SetLineColor(colors[idx % len(colors)])
    hists[hist_name].SetMinimum(1)    # Set minimum value for y-axis
    hists[hist_name].SetMaximum(1e8)  # Set maximum value for y-axis
    hists[hist_name].SetLineWidth(2)  # Set line width
    hists[hist_name].SetXTitle("MCParticle Prod Pos #theta [rad]")  # x-axis title

    if idx == 0:
        hists[hist_name].Draw()
    else:
        hists[hist_name].Draw("SAME")
    legend.AddEntry(hists[hist_name], names[idx], "l")

legend.Draw()

title = ROOT.TPaveText(0.2, 0.92, 0.8, 0.98, "NDC")
title.AddText("MCParticle Position Theta at Different Nozzle Blackhole Radii")
title.SetFillColor(0)
title.SetBorderSize(0)
title.SetFillColor(0)
title.SetTextAlign(22)
title.SetTextSize(0.04)
title.Draw()

c.SaveAs("MCParticle_Pos_Theta.png")
