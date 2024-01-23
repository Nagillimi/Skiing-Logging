import numpy as np

def quatMult(qa: np.ndarray, qb: np.ndarray):
    qa_w = qa[0]; qa_x = qa[1]; qa_y = qa[2]; qa_z = qa[3]
    qb_w = qb[0]; qb_x = qb[1]; qb_y = qb[2]; qb_z = qb[3]

    return np.array([
        qa_w*qb_w - qa_x*qb_x - qa_y*qb_y - qa_z*qb_z,  # w
        qa_w*qb_x + qa_x*qb_w + qa_y*qb_z - qa_z*qb_y,  # x
        qa_w*qb_y - qa_x*qb_z + qa_y*qb_w + qa_z*qb_x,  # y
        qa_w*qb_z + qa_x*qb_y - qa_y*qb_x + qa_z*qb_w,  # z
    ])