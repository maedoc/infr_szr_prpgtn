import numpy as np
# import lib.utils.stan
import glob
import os
import lib.plots.stan
import lib.io.stan
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import lib.utils.stan

# def check_completed(patient_ids, nchains, fname_suffix, root_dir):
#     with open(os.path.join(root_dir, 'chains_report.csv'), 'w') as fd:
#         for patient_id in patient_ids:
#             # szr_names = [
#             #     os.path.splitext(os.path.basename(fname))[0] for fname in glob.glob(
#             #         os.path.join(root_dir, patient_id, 'Rfiles', 'obs_data*.R'))
#             # ]
#             # Read EZ hypothesis or skip patient if hypothesis doesn't exist
#             try:
#                 ez_hyp = np.where(
#                     np.loadtxt(
#                         f'datasets/retro/{patient_id}/tvb/ez_hypothesis.destrieux.txt'
#                     ) == 1)[0]
#             except Exception as err:
#                 print(err)
#                 continue
#             print(patient_id)
#             fd.write(patient_id)
#             for szr_path in glob.glob(
#                     os.path.join(root_dir, patient_id, 'Rfiles', 'obs_data*.R')):
#                 szr_name = os.path.splitext(
#                     os.path.basename(szr_path))[0].split('obs_data_')[-1]
#                 csv_paths = []
#                 for i in range(nchains):
#                     log_path = os.path.join(root_dir, patient_id, 'logs',
#                                             f'{szr_name}_{fname_suffix}{i+1}.log')
#                     csv_path = os.path.join(
#                         root_dir, patient_id, 'results',
#                         f'samples_{szr_name}_{fname_suffix}{i+1}.csv')
#                     if (lib.utils.stan.is_completed(log_path)):
#                         csv_paths.append(csv_path)
#                 fd.write(f',{szr_name},{len(csv_paths)}')
#             fd.write('\n')


# def make_plots():
#     for patient_id in patient_ids:
#         # szr_names = [
#         #     os.path.splitext(os.path.basename(fname))[0] for fname in glob.glob(
#         #         os.path.join(root_dir, patient_id, 'Rfiles', 'obs_data*.R'))
#         # ]
#         # Read EZ hypothesis or skip patient if hypothesis doesn't exist
#         try:
#             ez_hyp = np.where(
#                 np.loadtxt(
#                     f'datasets/retro/{patient_id}/tvb/ez_hypothesis.destrieux.txt'
#                 ) == 1)[0]
#         except Exception as err:
#             print(err)
#             continue
#         print(patient_id)
#         for szr_path in glob.glob(
#                 os.path.join(root_dir, patient_id, 'Rfiles', 'obs_data*.R')):
#             szr_name = os.path.splitext(
#                 os.path.basename(szr_path))[0].split('obs_data_')[-1]
#             print(szr_name)
#             csv_paths = []
#             for i in range(nchains):
#                 log_path = os.path.join(root_dir, patient_id, 'logs',
#                                         f'{szr_name}_{fname_suffix}{i+1}.log')
#                 csv_path = os.path.join(
#                     root_dir, patient_id, 'results',
#                     f'samples_{szr_name}_{fname_suffix}{i+1}.csv')
#                 if (lib.utils.stan.is_completed(log_path)):
#                     csv_paths.append(csv_path)
#             if (len(csv_paths) == 0):
#                 continue
#             fit_data = lib.io.stan.rload(szr_path)
#             samples = lib.io.stan.read_samples(
#                 csv_paths, nwarmup=0, nsampling=200)
#             lib.plots.stan.x0_violin_patient(
#                 samples['x0'],
#                 ez_hyp,
#                 figsize=(25, 5),
#                 figname=os.path.join(root_dir, patient_id, 'figures',
#                                      f'x0_violin_{szr_name}.png'),
#                 plt_close=True)
#             lib.plots.stan.nuts_diagnostics(
#                 samples,
#                 figsize=(15, 10),
#                 figname=os.path.join(root_dir, patient_id, 'figures',
#                                      f'nuts_diagnostics_{szr_name}.png'),
#                 plt_close=True)
#             lib.plots.stan.pair_plots(
#                 samples, ['K', 'tau0', 'amplitude', 'offset', 'alpha'],
#                 figname=os.path.join(root_dir, patient_id, 'figures',
#                                      f'params_pair_plots_{szr_name}.png'),
#                 sampler='HMC',
#                 plt_close=True)
#             lib.plots.stan.plot_source(
#                 samples['x'].mean(axis=0),
#                 samples['z'].mean(axis=0),
#                 ez_hyp, [],
#                 figname=os.path.join(
#                     root_dir, patient_id, 'figures',
#                     f'posterior_predicted_src_{szr_name}.png'),
#                 plt_close=True)
#             lib.plots.stan.plot_fit_target(
#                 {
#                     'slp': samples['mu_slp'].mean(axis=0),
#                     'snsr_pwr': samples['mu_snsr_pwr'].mean(axis=0)
#                 },
#                 fit_data,
#                 figname=os.path.join(
#                     root_dir, patient_id, 'figures',
#                     f'posterior_predicted_slp_{szr_name}.png'),
#                 plt_close=True)


# def extract_x0(patient_ids, nchains, fname_suffix, root_dir):
#     '''
#     Extracts x0 values from csv files and saves them in a numpy file
#     '''
#     for patient_id in patient_ids:
#         # Read EZ hypothesis or skip patient if hypothesis doesn't exist
#         try:
#             ez_hyp = np.where(
#                 np.loadtxt(
#                     f'datasets/retro/{patient_id}/tvb/ez_hypothesis.destrieux.txt'
#                 ) == 1)[0]
#         except Exception as err:
#             print(err)
#             continue
#         print(patient_id)
#         first_szr = True
#         for szr_path in glob.glob(
#                 os.path.join(root_dir, patient_id, 'Rfiles', 'obs_data*.R')):
#             # szr_name = os.path.splitext(
#             #     os.path.basename(szr_path))[0].split('obs_data_')[-1]
#             szr_name = os.path.splitext(
#                 os.path.basename(szr_path))[0]
#             print(szr_name)
#             csv_paths = []
#             for i in range(nchains):
#                 log_path = os.path.join(root_dir, patient_id, 'logs',
#                                         f'{szr_name}_{fname_suffix}{i+1}.log')
#                 csv_path = os.path.join(
#                     root_dir, patient_id, 'results',
#                     f'samples_{szr_name}_{fname_suffix}{i+1}.csv')
#                 if (lib.utils.stan.is_completed(log_path)):
#                     csv_paths.append(csv_path)
#             if (len(csv_paths) == 0):
#                 continue
#             fit_data = lib.io.stan.rload(szr_path)
#             samples = lib.io.stan.read_samples(
#                 csv_paths, nwarmup=0, nsampling=200, variables_of_interest=['x0'])
#             np.save(os.path.join(root_dir, patient_id, 'results', f'x0_{szr_name}.npy'), samples['x0'])
#             if(first_szr):
#                 x0_cumul = samples['x0']
#                 first_szr = False
#             else:
#                 x0_cumul = np.append(x0_cumul, samples['x0'], axis=0)
#         np.save(os.path.join(root_dir, patient_id, 'results', 'x0_cumul.npy'), x0_cumul)


def ez_pred(patient_ids, nchains, fname_suffix, root_dir, x0_threshold):
    for patient_id in patient_ids:
        # Read EZ hypothesis or skip patient if hypothesis doesn't exist
        try:
            ez_hyp = np.where(
                np.loadtxt(
                    f'datasets/retro/{patient_id}/tvb/ez_hypothesis.destrieux.txt'
                ) == 1)[0]
        except Exception as err:
            print(err)
            continue
        first_szr = True
        for szr_path in glob.glob(
                os.path.join(root_dir, patient_id, 'Rfiles', 'obs_data*.R')):
            # szr_name = os.path.splitext(
            #     os.path.basename(szr_path))[0].split('obs_data_')[-1]
            szr_name = os.path.splitext(
                os.path.basename(szr_path))[0]
            csv_paths = []
            for i in range(nchains):
                log_path = os.path.join(root_dir, patient_id, 'logs',
                                        f'{szr_name}_{fname_suffix}{i+1}.log')
                csv_path = os.path.join(
                    root_dir, patient_id, 'results',
                    f'samples_{szr_name}_{fname_suffix}{i+1}.csv')
                if (lib.utils.stan.is_completed(log_path)):
                    csv_paths.append(csv_path)
            if (len(csv_paths) == 0):
                continue
            # samples = lib.io.stan.read_samples(
            #     csv_paths, nwarmup=0, nsampling=200, variables_of_interest=['x0'])
            samples = np.load(os.path.join(
                root_dir, patient_id, 'results', f'x0_{szr_name}.npy'))
            if(first_szr):
                ez_pred = samples.mean(axis=0) > x0_threshold
                first_szr = False
            else:
                ez_pred = np.logical_or(
                    ez_pred, samples.mean(axis=0) > x0_threshold)
        np.save(os.path.join(root_dir, patient_id, 'ez_pred.npy'), ez_pred)


if (__name__ == '__main__'):
    root_dir = '/home/anirudh/Academia/projects/infer_szr_prpgtn/results/exp10/retro_results'
    patient_ids = dict()
    patient_ids['engel1'] = ['id001_bt', 'id003_mg', 'id004_bj', 'id010_cmn', 'id013_lk', 'id014_vc',
                             'id017_mk', 'id020_lma', 'id022_te', 'id025_mc', 'id030_bf', 'id039_mra', 'id050_sx']
    patient_ids['engel2'] = ['id021_jc', 'id027_sj', 'id040_ms']
    patient_ids['engel3'] = ['id007_rd', 'id008_dmc',
                             'id009_ba', 'id028_ca', 'id037_cg']
    patient_ids['engel4'] = ['id011_gr', 'id033_fc', 'id036_dm', 'id045_bc']
    patient_ids['engel3or4'] = patient_ids['engel3'] + patient_ids['engel4']
    patient_ids['engel2or3or4'] = patient_ids['engel2'] + \
        patient_ids['engel3'] + patient_ids['engel4']

    # # Precision-Recall curves for onset window threshold
    # engel_scores = ['engel1', 'engel2', 'engel3or4']
    # engel_scores_rmn = ['I', 'II', 'III and IV']
    # for i,es in enumerate(engel_scores):
    #     precision = []
    #     recall = []
    #     src_thrshld = 0
    #     onst_wndw_sz = np.arange(5, 100, 5, dtype=int)
    #     for onst_wndw_sz_ in onst_wndw_sz:
    #         p, r = lib.utils.stan.precision_recall(patient_ids[es], root_dir, src_thrshld, onst_wndw_sz_)
    #         precision.append(p)
    #         recall.append(r)
    #     plt.figure()
    #     plt.plot(recall, precision, color='black')
    #     plt.scatter(recall, precision, marker='x')
    #     # for j,wndw_sz in enumerate(onst_wndw_sz):
    #     #     plt.annotate(str(wndw_sz), (recall[j], precision[j]))
    #     plt.xlabel('Recall', fontsize=13)
    #     plt.ylabel('Precision', fontsize=13)
    #     plt.xticks(fontsize=12)
    #     plt.yticks(fontsize=12)
    #     # plt.xlim([0.14, 0.88])
    #     # plt.ylim([0.35, 0.88])
    #     plt.title('Engel score ' + engel_scores_rmn[i], fontsize=15)
    #     plt.show(block=False)

    # # Precision and recall curves plotted separately against onset window threshold
    # engel_scores = ['engel1', 'engel2', 'engel3or4']
    # engel_scores_rmn = ['I', 'II', 'III and IV']
    # fig = plt.figure(figsize=(15,5))
    # ax_prec = fig.add_subplot(121)
    # ax_rec = fig.add_subplot(122)
    # for i,es in enumerate(engel_scores):
    #     precision = []
    #     recall = []
    #     src_thrshld = 0
    #     onst_wndw_sz = np.arange(5, 100, 1, dtype=int)
    #     for onst_wndw_sz_ in onst_wndw_sz:
    #         p, r = lib.utils.stan.precision_recall(patient_ids[es], root_dir, src_thrshld, onst_wndw_sz_)
    #         precision.append(p)
    #         recall.append(r)
    #     ax_prec.plot(onst_wndw_sz, precision, label=f"Engel score {engel_scores_rmn[i]}")
    #     ax_rec.plot(onst_wndw_sz, recall, label=f"Engel score {engel_scores_rmn[i]}")
    # ax_prec.set_xlabel(r'Onset Tolerance($t_{\epsilon}$)', fontsize=15)
    # ax_prec.set_ylabel('Precision', fontsize=15)
    # ax_prec.legend(frameon=False, loc='upper right')
    # ax_prec.set_xticks(np.r_[10:100:10])
    # ax_prec.set_xticklabels(map(str, np.r_[10:100:10]), fontsize=15)
    # ax_prec.set_yticks(np.r_[0.1:0.9:0.1])
    # ax_prec.set_yticklabels(map(lambda x: round(x, 1), np.r_[0.1:0.9:0.1]), fontsize=15)
    # ax_prec.spines['top'].set_visible(False)
    # ax_prec.spines['right'].set_visible(False)
    # ax_rec.set_xlabel(r'Onset Tolerance($t_{\epsilon}$)', fontsize=15)
    # ax_rec.set_ylabel('Recall', fontsize=15)
    # ax_rec.set_xticks(np.r_[10:100:10])
    # ax_rec.set_xticklabels(map(str, np.r_[10:100:10]), fontsize=15)
    # ax_rec.set_yticks(np.r_[0.1:0.9:0.1])
    # ax_rec.set_yticklabels(map(lambda x: round(x, 1), np.r_[0.1:0.9:0.1]), fontsize=15)
    # ax_rec.spines['top'].set_visible(False)
    # ax_rec.spines['right'].set_visible(False)
    # plt.tight_layout()

    # # precision = []
    # # recall = []
    # # src_thrshld = 0
    # # onst_wndw_sz =  np.arange(1, 100, dtype=int)
    # # for onst_wndw_sz_ in onst_wndw_sz:
    # #     p, r = lib.utils.stan.precision_recall(patient_ids['engel2or3or4'], root_dir, src_thrshld, onst_wndw_sz_)
    # #     precision.append(p)
    # #     recall.append(r)
    # # plt.figure()
    # # plt.plot(recall, precision, color='black')
    # # # for i,wndw_sz in enumerate(onst_wndw_sz):
    # # #     plt.annotate(str(wndw_sz), (recall[i], precision[i]))
    # # plt.xlabel('Recall', fontsize=13)
    # # plt.ylabel('Precision', fontsize=13)
    # # plt.xticks(fontsize=12)
    # # plt.yticks(fontsize=12)
    # # plt.title('Engel score II, III and IV', fontsize=15)
    # # plt.show(block=False)

    # # Bar plot
    # precision = []
    # recall = []
    # engel_scores = ['engel1', 'engel2', 'engel3or4']
    # ax = plt.subplot(111)
    # for i,scr in enumerate(engel_scores):
    #     src_thrshld = 0
    #     onst_wndw_sz = 10
    #     p, r = lib.utils.stan.precision_recall(patient_ids[scr], root_dir, src_thrshld, onst_wndw_sz)
    #     precision.append(p)
    #     recall.append(r)
    #     ax.bar([5*i + 1, 5*i + 2], [precision[i], recall[i]], color=['black', 'grey'])

    # # precision = []
    # # recall = []
    # # onst_thrshlds = [-0.05]
    # # for threshold in onst_thrshlds:
    # #     find_ez(threshold, patient_ids['engel2or3or4'], root_dir)
    # #     p, r = precision_recall(patient_ids['engel2or3or4'], root_dir)
    # #     precision.append(p)
    # #     recall.append(r)

    # # ax.bar([5,6], [precision[0],recall[0]], color=['black', 'grey'])
    # ax.set_xticks([np.mean([5*i + 1, 5*i + 2]) for i in range(len(engel_scores))])
    # ax.set_xticklabels(['I', 'II', 'III and IV'], fontsize=15)
    # ax.set_xlabel('Engel Score', fontsize=15)
    # ax.tick_params(axis='y', labelsize=12)
    # ax.spines['top'].set_visible(False)
    # ax.spines['right'].set_visible(False)
    # legend_elements = [Line2D([0], [0], color='black', lw=5, label='Precision'),
    #                    Line2D([0], [0], color='grey', lw=5, label='Recall')]
    # ax.legend(handles=legend_elements, frameon=False)
    # plt.show()

    # Box plot
    engel_scores = ['engel1', 'engel2', 'engel3or4']
    engel_labels = {'engel1': 'Engel I',
                    'engel2': 'Engel II', 'engel3or4': 'Engel III/IV'}
    precision = dict()  # []
    recall = dict()  # []
    cdf_prcsn = dict()
    cdf_recall = dict()
    fig = plt.figure(figsize=(20, 5))
    ax_bxplt = fig.add_subplot(121)
    ax_cdf = fig.add_subplot(122)

    for i, score in enumerate(engel_scores):
        src_thrshld = 0
        onst_wndw_sz = 10
        precision[score] = []
        recall[score] = []
        # print(score)
        for subj_id in patient_ids[score]:
            p, r = lib.utils.stan.precision_recall(
                [subj_id], root_dir, src_thrshld, onst_wndw_sz)
            precision[score].append(p)
            recall[score].append(r)
            # print(f'\t {subj_id} \t precision = {p} \t recall = {r}')
        cdf_prcsn[score] = []
        cdf_recall[score] = []
        prcsn_arr = np.array(precision[score])
        recall_arr = np.array(recall[score])
        for p in np.arange(0, 1.1, 0.1):
            cdf_prcsn[score].append(
                np.count_nonzero(prcsn_arr <= p)/prcsn_arr.size)
            cdf_recall[score].append(np.count_nonzero(
                recall_arr <= p)/recall_arr.size)
        ax_cdf.plot(np.arange(0, 1.1, 0.02),
                    cdf_prcsn[score], label=engel_labels[score])
        # ax_bxplt.scatter((5*i+1)*np.ones(len(patient_ids[score])), precision[score], color='black', alpha=0.3)
        # ax_bxplt.scatter((5*i+2)*np.ones(len(patient_ids[score])), recall[score], color='black', alpha=0.3)

    ax_bxplt.boxplot([precision[score] for score in engel_scores],
                     positions=[5*i+1 for i in range(3)])
    ax_bxplt.boxplot([recall[score] for score in engel_scores],
                     positions=[5*i+2 for i in range(3)])
    ax_bxplt.violinplot([precision[score] for score in engel_scores],
                     positions=[5*i+1 for i in range(3)], widths=0.2)
    ax_bxplt.violinplot([recall[score] for score in engel_scores],
                     positions=[5*i+2 for i in range(3)], widths=0.2)

    ax_bxplt.set_xticks([np.mean([5*i + 1, 5*i + 2])
                         for i in range(len(engel_scores))])
    ax_bxplt.set_xticklabels(['I', 'II', 'III and IV'], fontsize=15)
    ax_bxplt.set_xlabel('Engel Score', fontsize=15)
    ax_bxplt.tick_params(axis='y', labelsize=12)
    ax_bxplt.tick_params(axis='x', labelsize=12)
    ax_bxplt.spines['top'].set_visible(False)
    ax_bxplt.spines['right'].set_visible(False)
    # legend_elements = [Line2D([0], [0], color='black', lw=5, label='Precision'),
    #                    Line2D([0], [0], color='grey', lw=5, label='Recall')]
    # ax.legend(handles=legend_elements, loc='upper right')

    ax_cdf.legend()
    plt.show()

    # tpr = []
    # fpr = []
    # onst_thrshld = -0.05
    # nbins = 50
    # bin_thrshld =  np.arange(1, nbins)
    # for bin_thrshld_ in bin_thrshld:
    #     find_ez(onst_thrshld, bin_thrshld_, nbins, patient_ids['engel1'], root_dir)
    #     tpr_, fpr_ = tpr_and_fpr(patient_ids['engel1'], root_dir)
    #     tpr.append(tpr_)
    #     fpr.append(fpr_)
    # plt.figure()
    # plt.plot(fpr, tpr)
    # plt.xlabel('False Positive Rate', fontsize=15)
    # plt.ylabel('True Positive Rate', fontsize=15)
    # plt.show()
