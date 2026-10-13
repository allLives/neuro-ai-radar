import json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
if (ROOT/'data/weeks/2026-W41.json').exists() or (ROOT/'data/index.json').exists():
    raise SystemExit('Seed refused: archive already exists; historical reports are immutable.')
# 本期为对话中2026 W41的精选存档。后续由自动工作流从原始元数据生成。
ROWS=[
('RoboJEPA: Scaling Robotic Latent World Models','Artem Zholus et al.','arXiv','2026-10-07','https://arxiv.org/abs/2610.10515','preprint','世界模型','重点精读','JEPA;具身智能;机器人','在12类机器人形态的数据上研究潜在世界模型的规模规律，并用潜在预测进行机器人规划。作者报告潜在预测误差与实际规划表现具有相关性。','能否用任务相关的潜在预测质量代替像素重构质量评估世界模型？'),
('Continual Learning without Continual Training','Nikita Narayanan et al.','arXiv','2026-10-07','https://arxiv.org/abs/2610.10379','preprint','持续学习','重点精读','元学习;持续学习;记忆','通过预先元学习的潜在概念模型，在参数冻结后使用新增证据进行贝叶斯式推断，以适应新类别和环境。','持续适应在什么情况下只需要推断，而不需要更新参数？'),
('Human claustrum neurons encode uncertainty and prediction errors during aversive learning','Mingyue Hu et al.','Nature Neuroscience','2026-10-06','https://doi.org/10.1038/s41593-026-02475-x','journal','自我与意识','重点精读','元认知;预测加工;神经机制','人类单神经元记录显示屏状核与前扣带皮层编码不确定性和预测误差，但在任务阶段和跨试次时间上的编码模式不同。','高级认知变量如何在不同脑区之间分工？'),
('Differential effects of visual and tactile deprivation on spatially modulated cells in the medial entorhinal cortex','Jiayi Tian et al.','Nature Communications','2026-10-06','https://doi.org/10.1038/s41467-026-78000-2','journal','认知地图','重点精读','认知地图;多模态;海马','通过小鼠内嗅皮层记录研究视觉和触觉剥夺，揭示不同感觉线索对空间调谐细胞的差异化影响。','多模态感觉可靠性如何塑造可迁移的空间表征？'),
('Cross-Embodiment Robot Foundation World Models with Latent Actions','Huang Huang et al.','arXiv','2026-10-07','https://arxiv.org/abs/2610.10846','preprint','具身智能','重点精读','跨身体;潜在动作;世界模型','以潜在动作对齐不同机器人形态，实现多身体数据联合建模并改善部分操作基准表现。','不同身体之间是否存在可复用的抽象动作结构？'),
('Inference and learning in sparse autoencoders as natural gradient flow','Hadi Vafaii et al.','arXiv','2026-10-05','https://arxiv.org/abs/2610.07389','preprint','理论与机制','重点精读','自由能;表征学习;自然梯度','以变分自由能形式统一稀疏特征推断与字典学习，探索循环推断和自然梯度带来的特征恢复收益。','自由能思想能否落实为可对照验证的学习算法？'),
('Modality-specific reactive and predictive responses in the human superior colliculus','Danlei Chen et al.','Nature Neuroscience','2026-10-07','https://doi.org/10.1038/s41593-026-02480-0','journal','具身智能','重点精读','预测加工;感觉运动;主动感知','7T fMRI 显示人类上丘对视觉和躯体感觉事件具有模态相关的反应与预测性模式。','低层感觉运动结构如何参与未来感觉事件预测？'),
('EmbodiedRSI: Active Continual Robot Learning Through Hypothesis-Guided Co-Evolution','Python Song et al.','arXiv','2026-10-07','https://arxiv.org/abs/2610.10498','preprint','持续学习','重点精读','主动学习;机器人;自我改进','将假设生成、主动实验、记忆组织和技能迭代结合，使机器人能够针对失败与不确定性收集经验。','能否用不确定性驱动学习与探索的切换？'),
('Neural Decoding as Cognitive Inference','Yi Guo et al.','arXiv','2026-10-08','https://arxiv.org/abs/2610.11923','preprint','脑机接口','重点精读','神经解码;贝叶斯推断;表征','尝试把神经解码构建为具有潜在认知状态和先验的推断问题，而非只做输入到标签的分类。','神经信号能否建立跨任务复用的认知状态空间？'),
('Tuned inhibitory control of neuronal firing thresholds explains predictive sensorimotor behavior','Jungryul Ahn et al.','Communications Biology','2026-10-05','https://doi.org/10.1038/s42003-026-11082-2','journal','理论与机制','重点精读','预测编码;神经抑制;学习机制','提出通过调节神经元放电阈值表达预测先验的候选机制，并结合模型与感觉运动任务进行验证。','贝叶斯预测能否映射到具体神经细胞机制？'),
('Sparse Planning in Visual World Models via Cost Gradients','Yingchen Xu & Edward Grefenstette','NeurIPS 2026（作者标注）','2026-10-07','https://arxiv.org/abs/2610.10274','preprint','世界模型','值得关注','世界模型;稀疏计算;规划','按规划目标梯度动态筛选空间 token，在一些任务中减少规划计算，揭示重要信息的任务依赖性。','世界模型是否应该按行动后果选择保留的信息？'),
('Spatiotemporal encoding signatures of covert speech revealed by source-localized EEG and fMRI','Wei Zhang et al.','Communications Biology','2026-10-06','https://doi.org/10.1038/s42003-026-11102-1','journal','脑机接口','值得关注','内部言语;EEG;fMRI','结合 EEG 源定位与 fMRI 研究无声内部言语的时空编码特征。','内部言语能否成为非侵入式脑机接口的解码目标？'),
('Multimodal LLMs Can Learn to Read Brain Signals: A Vision–Language Model for Unified Multi-Task EEG Decoding','Parastoo Azizeddin et al.','arXiv','2026-10-07','https://arxiv.org/abs/2610.09355','preprint','脑机接口','值得关注','EEG;多模态;基础模型','将 EEG 组织为视觉化输入，让视觉语言模型完成多种 EEG 分析任务。','通用多模态预训练是否能帮助构建神经信号基础模型？'),
('LSD reconfigures cortical dynamics through faster brain rhythms and increased fractal dimension','V. Subramani et al.','Communications Biology','2026-10-07','https://doi.org/10.1038/s42003-026-10629-7','journal','自我与意识','值得关注','意识状态;致幻剂;脑动力学','分析 LSD 条件下皮层振荡与信号复杂性的变化；不应将复杂性变化等同于意识机制的直接证明。','改变的意识状态为意识理论提供了哪些可测量变量？'),
('Adult hippocampal neurogenesis shapes ideomotor action control in mice','W. Barde et al.','Communications Biology','2026-10-07','https://doi.org/10.1038/s42003-026-11112-z','journal','认知地图','值得关注','海马;灵活行为;可塑性','讨论成年海马神经发生与小鼠目标导向行为和行动灵活性的关系。','海马可塑性是否有助于减少持续学习中的行为僵化？'),
('Thalamocortical credit routing from the basal ganglia and cerebellum: anatomical constraints and circuit principles','Sho Tanno et al.','bioRxiv','2026-10-08','https://doi.org/10.64898/2026.10.02.755501','preprint','理论与机制','值得关注','信用分配;小脑;神经学习','从神经环路结构出发讨论基底节、小脑与丘脑-皮层系统中的信用分配。','生物神经结构能否启发更局部、更高效的学习规则？'),
('MetaLearnNCA: Few-Shot Offline Meta-Learning via Interacting Neural Cellular Automata','Etienne Guichard & Stefano Nichele','arXiv','2026-10-06','https://arxiv.org/abs/2610.08479','preprint','持续学习','值得关注','元学习;元胞自动机;自组织','以相互作用的神经元胞自动机探索少样本元学习，关注局部动态的适应能力。','无中心的局部学习能否涌现通用归纳偏置？'),
('Workhorse: Learning Robust Whole-Body Humanoid Loco-Manipulation from Human Data','Songbo Hu et al.','arXiv','2026-10-06','https://arxiv.org/abs/2610.09117','preprint','具身智能','值得关注','人形机器人;动作迁移;模仿学习','用人类数据支持人形机器人的全身移动与操作能力，并结合控制系统完成动作执行。','人类与机器人之间的动作表示如何对齐？'),
('FreeEvolve: Learning to Evolve Beyond Fixed Loops','Lecheng Kong et al.','arXiv','2026-10-06','https://arxiv.org/abs/2610.09197','preprint','AGI与智能体','值得关注','自我改进;元搜索;优化','尝试让系统优化迭代搜索程序本身，而不仅是搜索出的候选结果。','改进策略是否能够跨任务迁移，而非过拟合评测？'),
('Game theory driven multi-agent framework mitigates language model hallucination','Runzhe Liu et al.','Nature Communications','2026-10-07','https://doi.org/10.1038/s41467-026-78213-5','journal','AGI与智能体','值得关注','模型幻觉;多智能体;推理','通过博弈论驱动的多智能体协作与训练改善特定领域模型的可靠性。','如何衡量模型知识推断的可信程度？'),
('A neuro-inspired computational framework for AGI: predictive coding, active inference and free energy minimisation','Lioba C. S. Berndt & Alexander D. Shaw','Frontiers in Human Neuroscience','2026-10-08','https://doi.org/10.3389/fnhum.2026.1917153','perspective','理论与机制','延伸阅读','自由能原理;AGI;主动推断','概念性地整合预测编码、主动推断与自由能最小化。论文主要是理论框架，不是 AGI 实验验证。','统一理论应如何转化为可证伪的算法假设？'),
('Characterizing the role of reasoning tokens in large language models as state over tokens','Mosh Levy et al.','Nature Machine Intelligence','2026-10-07','https://doi.org/10.1038/s42256-026-01303-y','perspective','自我与意识','延伸阅读','推理状态;元认知;可解释性','讨论推理 token 的计算状态功能，不应把语言输出直接等同于内部思维过程。','如何在不依赖语言自报告的情况下评估 AI 元认知？'),
('Learning to Learn a Language','Lennart Carstens-Behrens & Holger Fröhlich','arXiv','2026-10-05','https://arxiv.org/abs/2610.05879','preprint','持续学习','延伸阅读','元学习;语言习得;归纳偏置','研究通过元训练习得语言学习策略的可行性，与大规模语言预训练路线形成对照。','学习能力能否通过可迁移的归纳偏置获得？'),
('Embodied Turing Machines: Stateful Code for Robot Recursive Self-Improvement','Kairui Hu et al.','arXiv','2026-10-08','https://arxiv.org/abs/2610.12369','preprint','具身智能','延伸阅读','机器人;程序状态;自我改进','通过可执行代码与环境状态表示组织机器人策略迭代；不构成机器人具备意识的证据。','结构化状态能否帮助机器人高效迭代策略？'),
('When ‘I’ and ‘You’ blur: self–other distinction failure and empathy dysregulation in schizophrenia','C. Huang et al.','Translational Psychiatry','2026-10-09','https://doi.org/10.1038/s41398-026-04514-4','review','自我与意识','延伸阅读','自他区分;意识;社会认知','梳理精神分裂症中自我-他人区分、共情与临床症状之间的联系。','自我表征应被拆分为哪些可操作的层级？'),
]
levels={'重点精读':0,'值得关注':1,'延伸阅读':2}
articles=[]
for i,row in enumerate(ROWS,1):
    title,authors,venue,date,url,kind,category,level,tags,summary,angle=row
    articles.append(dict(id=f'w41-{i:02}',title=title,authors=authors,venue=venue,date=date,url=url,kind=kind,category=category,level=level,tags=tags.split(';'),summary=summary,angle=angle,origin='上期人工精选',evidence='摘要/元数据级别；建议以原文核对'))
deepdives=[
 dict(id='w41-01',headline='可预测 ≠ 对决策有用',insight='RoboJEPA 将潜在预测误差与机器人规划质量联系起来，但潜在表征是否保留低频、关键且难预测的任务信息，仍需专门实验检验。',experiment='比较纯预测 JEPA、任务相关信息约束 JEPA 与结构化表征模型，在背景干扰、奖励切换、稀有障碍任务中的迁移效率。'),
 dict(id='w41-02',headline='推断、检索与权重更新之间，谁来做选择？',insight='冻结参数、通过新证据推断的策略降低遗忘风险，但其适应范围受到元训练分布、上下文容量与记忆检索质量的限制。',experiment='在环境变化强度可控的 POMDP 中，比较持续微调、记忆推断和基于置信度的混合切换机制。'),
 dict(id='w41-04',headline='认知地图如何跨感官稳定？',insight='视觉或触觉缺失对空间细胞的影响随环境线索而异，说明空间表示可能依赖跨模态整合而非单一感官的特征。',experiment='构建视觉与触觉可分离的导航环境，测试跨感官遮蔽时地图拓扑、重新定位效率与下游导航性能。'),
 dict(id='w41-03',headline='不确定性是高阶内部状态',insight='屏状核与前扣带皮层可编码模型估计的预测误差与不确定性，但持续编码的时间特征不同。该结果不能直接证明相关脑区产生意识。',experiment='让智能体显式估计对自身状态信念的置信度，测试其是否提升噪声环境中的主动感知与任务迁移。'),
 dict(id='w41-06',headline='从宏大自由能原理走向具体算法',insight='通过循环推断与自然梯度讨论稀疏表征，可以对照测量机制级改进；但优化性能不能反推整个神经自由能理论成立。',experiment='在特征稀有程度和组合结构变化的连续学习任务上，比较标准 SAE、循环推断、自然梯度及组合模型。'),
]
issue=dict(id='2026-W41',title='预测、记忆与认知地图',subtitle='从潜在世界模型走向可迁移的内部表征',from_date='2026-10-05',to_date='2026-10-11',published_at='2026-10-13',edition=41,curation='人工精选·试刊',method_note='本期来自此前的文献速递对话，已部分核对原文；部分条目尚未完成逐篇元数据复核。后续自动版将保留来源与可靠性标记。',topline='世界模型不再只比谁预测得准；持续学习开始重新讨论“何时学习”以及认知地图如何跨感官形成。',articles=articles,deepdives=deepdives)
out=ROOT/'data/weeks/2026-W41.json';out.write_text(json.dumps(issue,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'data/index.json').write_text(json.dumps(dict(site='NeuroAI Radar',updated_at='2026-10-13',weeks=[dict(id=issue['id'],title=issue['title'],from_date=issue['from_date'],to_date=issue['to_date'],count=len(articles),curation=issue['curation'])]),ensure_ascii=False,indent=2),encoding='utf-8')
print('seeded',len(articles),'articles')
