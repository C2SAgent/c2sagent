# # 初始化
# from core.db.base import DatabaseManager
# from model.model_agent import AgentCard, Skill, UserConfig


# db = DatabaseManager('postgresql://postgres:postgre@localhost/manager_agent')

# # 查询单个用户
# user = db.fetch_one(UserConfig, name='testuser')

# # 查询所有agent card并按名称排序
# agents = db.fetch_all(AgentCard, order_by='name')

# # 复杂查询
# from sqlalchemy import or_
# conditions = [
#     AgentCard.name.like('%chat%'),
#     or_(
#         AgentCard.streaming == True,
#         AgentCard.version == '1.0'
#     )
# ]
# results = db.fetch_complex(AgentCard, conditions, order_by=['name', 'id'])

# # # 插入新记录
# # new_user = db.insert(UserConfig, {
# #     'name': 'super_admin',
# #     'password': 'super_admin',
# #     'core_llm_name': 'deepseek',
# #     'core_llm_url': 'https://api.deepseek.com/v1',
# #     'core_llm_key': 'sk-fc9e70085fe4411fb5b3f5aa121ee9a9'
# # })

# # 查询或插入
# skill, created = db.fetch_or_insert(Skill, 
#                                   {'name': 'new_skill'},
#                                   {'description': '默认描述'})

# user = db.fetch_all(UserConfig, {'name': 'super_admin'})
# print(user[0].password)